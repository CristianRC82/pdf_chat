# FastAPI langgraph

## Description

This project presents an endpoint built with FastAPI that processes requests to run Langgraph, allowing complex processing flows and task orchestration to be handled efficiently and scalably.

## Requirements

* git
* python version 3.11.9 or higher
* pyenv
* FastAPI
* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## compile project locally

It is essential to have Python version 3.11.9 or higher installed.

1. Install the Python version manager pyenv by following these installation guides

   * linux: [https://realpython.com/intro-to-pyenv/](https://)
   * windows: [https://pyenv-win.github.io/pyenv-win/](https://)
     If an error occurs where the Python version is not updated to the previously installed version, it is recommended to use the following commands
     * `pyenv versions` : List the Python versions installed via pyenv.
     * `pyenv global <version>` : Add the Python version installed via pyenv globally.
     * `pyenv local <version>` : Add the Python version installed via pyenv locally.
2. create and activate the virtual environment

   * linux: Open the terminal in the root directory of the service and run the following commands
     * `python3 -m venv <enviroment_name>`: created env
     * `source <enviroment_name/bin/activate>`: activate env
   * windows: Open PowerShell or CMD in the root directory of the service and run the following commands:
     * `python -m venv <enviroment_name>`: created env
     * In poweShell `.\enviroment_name\Scripts\Activate.ps1` : activate env
     * in cmd `.\enviroment_name\Scripts\Activate.bat`: activate env
3. Install uv [https://docs.astral.sh/uv/#highlights](https://), either for Windows or for Linux/Mac.
4. Once you have installed **uv**, you can open a new terminal and run the command `uv`, where you will see the **uv** command guide.
5. Once installed and verified that uv is installed correctly, you must run the following command `uv sync` to synchronize uv with the service dependencies.
6. Create a file in the root directory of the project named `.env` with the following content:

   ```
   PROJECT_NAME=
   FIRESTORE_EMULATOR_HOST=
   AZURE_OPENAI_API_KEY = 
   AZURE_OPENAI_API_VERSION=
   AZURE_INSTANCE_NAME =
   AZURE_OPENAI_DEPLOYMENT_NAME =
   AZURE_OPENAI_ENDPOINT =

   #AZURE_OPENAI_API_KEY_o3_MINI =
   AZURE_OPENAI_API_VERSION_o3_MINI=
   AZURE_INSTANCE_NAME_o3_MINI = 
   AZURE_OPENAI_DEPLOYMENT_NAME_o3_MINI =
   AZURE_OPENAI_ENDPOINT_o3_MINI =


   LANGFUSE_SECRET_KEY=
   LANGFUSE_PUBLIC_KEY=
   LANGFUSE_HOST=
   ```
7. Install the Google SDK, which will allow you to authenticate with your company email account for a specific GCP project.[[https://cloud.google.com/sdk/docs/install?hl=es-419](https://)
8. Request permissions from the infrastructure department for the BigQuery service using your corporate email account.
9. Once you have the necessary permissions, you must log in from the Google SDK.
10. Finally, from the project terminal, you can run the command `uv run fastapi dev` and, if everything went well, you will be able to access this link. [http://127.0.0.1:8000/docs](https://)

## General Workflow

The workflow is as follows

1. The client makes an HTTP request to the FastAPI endpoint.
2. The endpoint receives and validates the incoming request.
3. The Langrap graph is constructed and executed according to the parameters received.
4. The graph processes the defined tasks and flows, orchestrating calls and computations.
5. Once completed, the result of the graph is returned in the HTTP response.
6. The client receives the processed data to continue with its logic or visualization.
