-----

# LLM-Gmail

-----

## Overview

**LLM-Gmail** is an innovative tool designed to help you efficiently manage your email inbox by providing concise summaries of your Gmail messages. What sets LLM-Gmail apart is its commitment to **privacy and local processing**: it leverages Large Language Models (LLMs) to summarize your emails *without sending your data to public APIs* like ChatGPT or Gemini.

This is achieved by integrating with **Ramalama**, an open-source project that allows you to containerize and run Ollama instances locally. This gives you full control over the LLM model used for summarization, letting you choose based on your specific needs and the capabilities of your local machine.

-----

## Features

  * **Secure Gmail Integration:** Connects to your Gmail account to fetch message content.
  * **Local LLM Summarization:** Summarizes email content using LLMs running entirely on your local machine.
  * **Enhanced Privacy:** Your email data never leaves your environment for LLM processing.
  * **Flexible Model Choice:** Select and run the LLM model that best suits your requirements and hardware limitations, thanks to Ramalama/Ollama.
  * **No Public API Dependency:** Freedom from reliance on external API costs, rate limits, or service availability.

-----

## Why LLM-Gmail?

In an era of overflowing inboxes and increasing data privacy concerns, LLM-Gmail offers a powerful, confidential solution:

  * **Uncompromised Privacy:** Keep your sensitive communications private by processing summaries locally.
  * **Total Control:** You decide which LLM model to use, tailoring the experience to your preferences for speed or accuracy.
  * **Cost-Effective:** Avoid ongoing subscription fees associated with public LLM APIs.
  * **Empowerment:** Take back control over your email summaries and data.

-----

## How It Works

LLM-Gmail connects to your Gmail account via Google's official APIs (for email retrieval). The retrieved email content is then passed to your local Ramalama/Ollama instance, which performs the summarization. The entire LLM processing happens on your machine.

-----

## Getting Started

### Prerequisites

  * Python 3.x
  * A Gmail account with API access configured (instructions below).
  * Sufficient local resources (CPU/GPU and RAM) for running your chosen LLM.
  * **uv**: Follow the official installation guide for `uv` [here](https://docs.astral.sh/uv/getting-started/installation/).
  * **Podman or Docker** (recommended for running Ramalama, though Ramalama will attempt to run models directly if neither is installed).

### Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sbauza/llm-gmail.git
    cd llm-gmail
    ```
2.  **Configure Gmail API:**
    To allow LLM-Gmail to access your Gmail account, you need to set up Google's Gmail API. Follow the official guide to enable the API, create credentials, and download your `credentials.json` file:
    [https://developers.google.com/workspace/gmail/api/quickstart/python](https://developers.google.com/workspace/gmail/api/quickstart/python)
    **Place the downloaded `credentials.json` file in the root directory of this project.**

### Running LLM-Gmail

Follow these steps to get LLM-Gmail up and running:

1.  **Choose your LLM Model:**
    Select a suitable LLM model from [Ollama's website](https://www.ollama.com/) or another registry like Huggingface. Refer to the [Ramalama documentation](https://github.com/containers/ramalama/blob/main/docs/ramalama-serve.1.md) for more details on supported models and registries.

2.  **Start the Ramalama Container:**
    Replace `<container_name>` with a name for your container and `<model_name>` (e.g., `'mistral'`) with your chosen LLM model.

    ```bash
    uv run ramalama serve -d -p 8080 --name <container_name> <model_name>
    ```

3.  **Run LLM-Gmail:**
    Execute the main LLM-Gmail script.

    ```bash
    uv run main.py
    ```

    This will connect to your Gmail, fetch messages, and start summarizing them using your local Ramalama instance.

-----

## Contributing

We welcome contributions\! If you have ideas for new features, bug fixes, or improvements, please feel free to:

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

-----

## License

This project is licensed under the [Apache 2.0 License](https://github.com/sbauza/llm-gmail/blob/main/LICENSE) - see the `LICENSE` file for details.

-----

## Contact

Sylvain Bauza - sbauza@free.fr

Project Link: [https://github.com/sbauza/llm-gmail](https://www.google.com/search?q=https://github.com/sbauza/llm-gmail)

-----
