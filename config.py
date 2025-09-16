#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # Azure AI Foundry Configuration (unified for Voice Live and Agent)
    AI_FOUNDRY_ENDPOINT = os.environ.get("AI_FOUNDRY_ENDPOINT", "")  # e.g., https://aif-general-dev-001.services.ai.azure.com
    AI_FOUNDRY_PROJECT_NAME = os.environ.get("AI_FOUNDRY_PROJECT_NAME", "")
    AI_FOUNDRY_AGENT_ID = os.environ.get("AI_FOUNDRY_AGENT_ID", "")
    AI_FOUNDRY_API_KEY = os.environ.get("AI_FOUNDRY_API_KEY", "")
    AI_FOUNDRY_API_VERSION = os.environ.get("AI_FOUNDRY_API_VERSION", "2025-05-01-preview")
    
    # Azure AI Services Configuration (fallback for when AI Foundry is not available)
    AI_PROJECT_CONNECTION_STRING = os.environ.get("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    AI_MODEL_DEPLOYMENT_NAME = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    AI_ENDPOINT = os.environ.get("AZURE_AI_ENDPOINT", "")
    AI_API_KEY = os.environ.get("AZURE_AI_API_KEY", "")