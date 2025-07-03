import datetime
import json
import logging
import os.path
from typing import List

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
LAST_RUN_FILE = "last_run.json"

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


def get_last_run_time() -> datetime:
    """Gets the last run time from file or returns a default time."""
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as last_run_f:
            data = json.load(last_run_f)
            return datetime.datetime.fromisoformat(data['last_run'])
    return datetime.datetime.now() - datetime.timedelta(days=7)  # Default to 7 days ago if no last run


def build_query(last_run: datetime) -> str:
    """Builds the query string for fetching emails."""
    return f"is:unread after:{last_run.strftime('%Y/%m/%d')}"


def callback_fetch_email(id, response, exception):
    if exception is not None:
        print(exception)
    else:
        email = {}
        email['snippet'] = response['snippet']
        title_and_from = filter(lambda dct: dct['name'] in ['Subject', 'From'], response['payload']['headers'])
        for header in title_and_from:
            if header['name'] == 'Subject':
                email['subject'] = header['value']
            else:
                email['from'] = header['value']
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
        batch.add(gmail.users().messages().get(userId="me", id=message['id']))
    batch.execute()
    return EMAIL_CACHE

def get_labels(gmail: Resource) -> List[str]:
    results = gmail.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
        print("No labels found.")
        return
    return labels


def call_ramalama_api(api, method, data=None):
    if method == 'post':
        payload = {"prompt": data,"n_predict": 128}
        r = requests.post('http://127.0.0.1:8080/'+api, data=json.dumps(payload))
        return r.json()


CATEGORY_LABELS = [
    'JIRA',
    'OpenStack Gerrit',
    'rhos-compute',
    'Other'
]

def categorize_email_with_ollama(email_content: str) -> str:
    """Categorizes an email using the local Ollama LLM."""
    try:
        system_prompt = f"""I give you a list of categories :
            {', '.join(CATEGORY_LABELS)}. Return me only the name of the
            category from that list that can match the following phrase :
        """


        response = call_ramalama_api('completion', 'post', prompt + email_content)
        print(response)
        response_content = print(response['content'])
        try:
            category = json.loads(response_content)['category']
        except Exception:
            return
        return category if response_content in CATEGORY_LABELS else "Other"
    except Exception as e:
        logging.error(f"Error in Ollama categorization: {str(e)}")
        return "Other"

def main():
    client = gmail_client()
    emails = fetch_emails(client, build_query(datetime.datetime.now() - datetime.timedelta(minutes=1)))
    for email in emails:
        print(categorize_email_with_ollama(email['subject'] + '\n' + email['snippet']))

if __name__ == "__main__":
    main()

