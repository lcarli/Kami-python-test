# Usage — Kami Python Test

This page explains how to set up and run the project locally on Windows using PowerShell (`pwsh.exe`). It assumes you have Python 3.10+ and `pip` available.

1. Create and activate a virtual environment

PowerShell commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Environment configuration — exact names

This project reads configuration from environment variables (and `python-dotenv` is loaded by `config.py`). Use a `.env` file or set variables in your PowerShell session. The variables used by `config.py` include:

- `MicrosoftAppId` — Bot Framework application ID (optional).
- `MicrosoftAppPassword` — Bot Framework application password (optional).
- `AI_FOUNDRY_ENDPOINT` — AI Foundry endpoint, e.g. `https://<your-foundry>.services.ai.azure.com`.
- `AI_FOUNDRY_PROJECT_NAME` — AI Foundry project name.
- `AI_FOUNDRY_AGENT_ID` — AI Foundry agent identifier.
- `AI_FOUNDRY_API_KEY` — API key for AI Foundry.
- `AI_FOUNDRY_API_VERSION` — API version (default `2025-05-01-preview`).
- `AZURE_AI_PROJECT_CONNECTION_STRING` — Connection string for Azure AI projects (fallback option).
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` — Model deployment name (default `gpt-4o`).
- `AZURE_AI_ENDPOINT` — Azure OpenAI / Azure AI endpoint.
- `AZURE_AI_API_KEY` — API key for Azure OpenAI / Azure AI (if using key-based auth).

Create a `.env` example (place at the repository root):

```text
# .env example
MicrosoftAppId=
MicrosoftAppPassword=
AI_FOUNDRY_ENDPOINT=https://your-foundry.services.ai.azure.com
AI_FOUNDRY_PROJECT_NAME=your-project
AI_FOUNDRY_AGENT_ID=your-agent-id
AI_FOUNDRY_API_KEY=your-foundry-api-key
AI_FOUNDRY_API_VERSION=2025-05-01-preview
AZURE_AI_PROJECT_CONNECTION_STRING=
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
AZURE_AI_ENDPOINT=https://your-azure-ai-endpoint
AZURE_AI_API_KEY=your-azure-api-key
```

Set variables in the current PowerShell session (example):

```powershell
$env:AZURE_AI_ENDPOINT = 'https://your-azure-ai-endpoint'
$env:AZURE_AI_API_KEY = 'xxxx'
$env:AI_FOUNDRY_API_KEY = 'yyyy'
```

3. Authentication examples (Azure SDK)

The repository uses environment variables by default, but you can authenticate to Azure services in two common ways.

- Key-based authentication (explicit API key):

```python
import os
from azure.ai.openai import OpenAIClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ.get('AZURE_AI_ENDPOINT')
key = os.environ.get('AZURE_AI_API_KEY')
client = OpenAIClient(endpoint, AzureKeyCredential(key))
```

- Managed identity or developer credentials (DefaultAzureCredential):

```python
import os
from azure.ai.openai import OpenAIClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ.get('AZURE_AI_ENDPOINT')
credential = DefaultAzureCredential()
client = OpenAIClient(endpoint, credential)
```

Notes:

- If you use `DefaultAzureCredential`, ensure your environment or host provides credentials (Visual Studio Code sign-in, Azure CLI `az login`, or an assigned managed identity in Azure). See `doc/microsoft_references.md` for links to auth docs.
- `config.py` is already loading `.env` via `dotenv.load_dotenv()`, so a `.env` file at the repo root is sufficient for local development.

4. Run services

- To run the voice live service:

```powershell
python voice_live_service.py
```

- To run the AI agent service:

```powershell
python ai_agent_service.py
```

- To run the bot logic:

```powershell
python bot.py
```

- To start everything (development convenience):

```powershell
python start_all.py
```

5. Troubleshooting

- Ports in use: If a service fails to bind to a port, check which process is using it with PowerShell commands such as `Get-NetTCPConnection -LocalPort <port>` and inspect `OwningProcess`.
- Missing dependencies: Ensure the virtual environment is activated and `pip install -r requirements.txt` completed successfully.
- Missing/invalid API key: Confirm the correct environment variables are set in the same PowerShell session that runs the scripts.

6. Testing suggestions

- Add a small `pytest` suite for message handler logic and a smoke test that imports modules and verifies that services start without crashing.
