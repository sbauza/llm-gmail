import base64
import datetime
import email as email_lib
import json
import html
import logging
import os.path
import re
from typing import List

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

EMAIL_CACHE = []

def gmail_client() -> Resource:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
    except HttpError as error:
        logging.error(f"Failed to call the Gmail API: {error}")
    return service


def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ')
    return html.unescape(text).strip()


def parse_email(mime_content):
    msg = email_lib.message_from_string(mime_content)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            body = part.get_payload(decode=True)
            if 'html' in content_type:
                return extract_text(body.decode())
    else:
        return extract_text(msg.get_payload(decode=True))


def callback_fetch_email(id, message, exception):
    if exception is not None:
        print(exception)
    else:
        email = {}
        msg = email_lib.message_from_bytes(
            base64.urlsafe_b64decode(message['raw']))
        email['body'] = ''

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                body = part.get_payload(decode=True)
                if 'html' in content_type:
                    email['body'] += extract_text(body.decode())
        else:
            email['body'] += extract_text(msg.get_payload(decode=True))


        email['from'] = msg['from']
        email['subject'] = msg['subject']
        email['to'] = msg['to']

        EMAIL_CACHE.append(email)


def fetch_emails(gmail: Resource, query: str) -> List[dict]:
    """Fetches emails based on the given query."""
    global EMAIL_CACHE
    EMAIL_CACHE = []
    try:
        results = gmail.users().messages().list(userId="me", q=query).execute()
    except HttpError as error:
        logging.error(f"Failed to fetch emails: {error}")
        raise
    message_ids = results.get("messages", [])
    batch = gmail.new_batch_http_request(callback=callback_fetch_email)
    for message in message_ids:
        batch.add(gmail.users().messages().get(userId="me", id=message['id'],
                                               format='raw'))
    batch.execute()
    return EMAIL_CACHE


def call_ramalama_api(api, method, data=None):
    if method == 'post':
        payload = {"prompt": data,"n_predict": 128}
        r = requests.post('http://127.0.0.1:8080/'+api, data=json.dumps(payload))
        return r.json()


def summarize_email_with_ollama(email_content: str) -> str:
    """Summarizes an email using the local Ollama LLM."""
    try:
        system_prompt = f"""Please give me a short summary (like 3 phrases) of
        the following email content which is actually a python dictionary
        containing the subject, the From value, the To value and the decoded
        body which can be HTML-formatted :
        """


        response = call_ramalama_api('completion', 'post', system_prompt + str(email_content))
        print(response['content'])
    except Exception as e:
        logging.error(f"Error in Ollama categorization: {str(e)}")
        return "Other"


def main():
    client = gmail_client()
    date = datetime.datetime.now() - datetime.timedelta(days=2)
    gmail_query = (f"is:unread is:starred " +
                   f"in:inbox after:{round(date.timestamp())}")
    emails = fetch_emails(client, gmail_query)
    for email in emails:
        print('-------------------------------------------------------')
        print(f'From: {email['from']}, Subject: {email['subject']}')
        summarize_email_with_ollama(email)
        print('-------------------------------------------------------\n\n\n')


if __name__ == "__main__":
    main()

