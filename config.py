#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # Azure Speech Service Configuration
    SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY", "")
    SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "")
    
    # Voice Live API Configuration 
    VOICE_LIVE_ENDPOINT = os.environ.get("AZURE_VOICE_LIVE_ENDPOINT", "")
    VOICE_LIVE_KEY = os.environ.get("AZURE_VOICE_LIVE_KEY", "")
    
    # Azure AI Foundry Configuration
    AI_PROJECT_CONNECTION_STRING = os.environ.get("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    AI_MODEL_DEPLOYMENT_NAME = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    AI_ENDPOINT = os.environ.get("AZURE_AI_ENDPOINT", "")
    AI_API_KEY = os.environ.get("AZURE_AI_API_KEY", "")