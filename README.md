# AI-Powered Voice Bot with Azure AI Foundry and Speech Service

This repository contains an AI-powered bot built using the Microsoft Bot Framework SDK for Python with integrated Azure AI Foundry and Azure Speech Service capabilities, following the [official Microsoft quickstart guide](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?tabs=python&pivots=fdp-project).

## Features

- **AI Agent**: Provides intelligent responses using Azure AI Foundry instead of simple echoing
- **Voice Processing**: Speech-to-text and text-to-speech capabilities using Azure Speech Service
- **Voice Live Agents**: Real-time voice interaction support with AI responses
- **Audio Message Support**: Can process audio attachments and respond with voice
- **Multiple Voice Options**: Access to various neural voices from Azure
- **Conversation History**: Maintains context across conversation turns
- **Welcome Message**: Greets new users and explains AI and voice capabilities
- **Error Handling**: Comprehensive error handling with debugging support
- **Fallback Responses**: Graceful degradation when AI services are not configured
- **Bot Framework Integration**: Uses the official Microsoft Bot Framework SDK

## Prerequisites

Before setting up the bot locally, ensure you have:

- **Python 3.6 or higher** - Check with `python --version` or `python3 --version`
- **pip package manager** - Usually comes with Python, check with `pip --version`
- **Git** - For cloning the repository
- **Bot Framework Emulator** (optional) - For testing the bot locally
- **Azure AI Foundry Setup** - For intelligent AI responses (see configuration section)
- **Azure Speech Service** - For voice capabilities (see configuration section)

### Azure AI Foundry Setup

To enable intelligent AI responses, you need an Azure AI Foundry resource:

1. **Create Azure AI Hub and Project**:
   - Go to [Azure AI Foundry](https://ai.azure.com/)
   - Create a new AI hub or use an existing one
   - Create a project within the hub
   - Deploy a chat model (e.g., gpt-4o-mini)

2. **Get Connection Information**:
   - Note the **Endpoint URL** from your AI project
   - Get the **API Key** from the project settings
   - Note the **Model Deployment Name** you want to use

### Azure Speech Service Setup

To enable voice capabilities, you need an Azure Speech Service resource:

1. **Create Azure Speech Service**:
   - Go to the [Azure Portal](https://portal.azure.com/)
   - Create a new "Speech Service" resource
   - Note the **Key** and **Region** from the resource

2. **Get AI Foundry Access** (Optional for advanced features):
   - Visit [AI Foundry](https://ai.azure.com/)
   - Create or access your AI hub
   - Get endpoint and key information

### Verifying Prerequisites

```bash
# Check Python version
python --version  # or python3 --version

# Check pip version
pip --version

# Check Git version
git --version
```

## Local Development Setup

### 1. Clone and Navigate to Repository

```bash
git clone https://github.com/lcarli/Kami-python-test.git
cd Kami-python-test
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

The bot uses environment variables for configuration. For local development, basic bot functionality works with fallback responses, but AI features require Azure AI Foundry setup and voice features require Azure Speech Service setup.

### Environment Variables

| Variable | Description | Default | Required for AI |
|----------|-------------|---------|----------------|
| `MicrosoftAppId` | Bot application ID from Azure | `""` (empty) | No |
| `MicrosoftAppPassword` | Bot application password from Azure | `""` (empty) | No |
| `PORT` | Server port | `3978` | No |
| `AZURE_AI_ENDPOINT` | Azure AI Foundry endpoint URL | `""` (empty) | **Yes** |
| `AZURE_AI_API_KEY` | Azure AI Foundry API key | `""` (empty) | **Yes** |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | AI model deployment name | `gpt-4o-mini` | No |
| `AZURE_SPEECH_KEY` | Azure Speech Service subscription key | `""` (empty) | For Voice |
| `AZURE_SPEECH_REGION` | Azure Speech Service region | `""` (empty) | For Voice |
| `AZURE_VOICE_LIVE_ENDPOINT` | Voice Live endpoint (optional) | `""` (empty) | No |
| `AZURE_VOICE_LIVE_KEY` | Voice Live key (optional) | `""` (empty) | No |

### Local Development Configuration

For basic bot testing, you can run without any environment variables. The bot will use fallback responses when AI services are not configured.

#### AI Features Configuration

To enable intelligent AI responses, you **must** set the Azure AI Foundry credentials:

```bash
# Required for AI features
export AZURE_AI_ENDPOINT="https://your-project.cognitiveservices.azure.com/"
export AZURE_AI_API_KEY="your_ai_api_key"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
```

#### Voice Features Configuration

To enable voice capabilities, you **must** set the Azure Speech Service credentials:

```bash
# Required for voice features
export AZURE_SPEECH_KEY="your_speech_service_key"
export AZURE_SPEECH_REGION="your_speech_service_region"  # e.g., "eastus"
```

#### Complete .env File Example

Create a `.env` file (not tracked by git) for local development:

```bash
# .env file - Basic bot configuration (optional)
MicrosoftAppId=
MicrosoftAppPassword=
PORT=3978

# Azure AI Foundry (required for intelligent responses)
AZURE_AI_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_AI_API_KEY=your_ai_api_key_here
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Azure Speech Service (required for voice features)
AZURE_SPEECH_KEY=your_speech_service_key_here
AZURE_SPEECH_REGION=eastus

# AI Foundry Voice Live (optional for advanced features)
AZURE_VOICE_LIVE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VOICE_LIVE_KEY=your_voice_live_key_here
```

## Running the Bot Locally

### Option 1: Using the main application (app.py)

```bash
python app.py
```

### Option 2: Using the startup script (start_bot.py)

The startup script provides more user-friendly output:

```bash
python start_bot.py
```

### Expected Output

When the bot starts successfully, you should see:

```
Starting Echo Bot...
Bot will be available at: http://localhost:3978/api/messages
Press CTRL+C to stop the bot
======== Running on http://localhost:3978 ========
(Press CTRL+C to quit)
```

The bot will be running and listening for messages on `http://localhost:3978/api/messages`.

## Testing the Bot

### Running Unit Tests

The project includes unit tests to verify bot functionality:

```bash
# Run all tests
python test_bot.py

# For verbose output
python -m unittest test_bot.py -v
```

### Testing AI Features

The enhanced bot includes several AI-powered features:

1. **Basic Text Interaction**: Send any text message to get an intelligent AI response
2. **Voice Commands**:
   - `/voice` - Enable voice session for voice responses  
   - `/voices` - List available neural voices
   - `/help` - Show all available commands and service status
3. **Audio Messages**: Send audio attachments to test speech-to-text with AI responses (when properly configured)

### Testing with Bot Framework Emulator

1. **Download and install** the [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. **Start the bot** using one of the methods above
3. **Open Bot Framework Emulator**
4. **Connect to** `http://localhost:3978/api/messages`
5. **Test basic functionality**: Send text messages and see AI-powered responses
6. **Test voice commands**: Try `/voice`, `/voices`, and `/help` commands
7. **Monitor console output** for AI service and voice service status messages

### Testing Voice Features with Real Audio

To test audio processing (requires Azure Speech Service configuration):

1. **Configure speech service** as described in the Configuration section
2. **Start the bot** with voice features enabled
3. **Send `/voice` command** to enable voice session
4. **Use audio recording tools** or Bot Framework Emulator's microphone feature
5. **Send audio messages** to test speech-to-text functionality

Note: Full audio testing requires proper audio codec support and may work better with deployed bots rather than local emulator testing.

### Testing with ngrok (for external testing)

If you need to test the bot from external sources or webhooks:

1. **Install** [ngrok](https://ngrok.com/)
2. **Start the bot**: `python app.py`
3. **In another terminal, run**: `ngrok http 3978`
4. **Use the ngrok URL** (e.g., `https://abcd1234.ngrok.io/api/messages`) for external testing

## Development Workflow

### Making Changes

1. **Make your changes** to the bot code
2. **Run tests** to ensure functionality: `python test_bot.py`
3. **Test locally** using the Bot Framework Emulator
4. **Commit your changes**

### Debugging

- **Console Output**: The bot logs information to the console, including errors and voice service status
- **Bot Framework Emulator**: Shows detailed conversation flow and errors
- **Error Handling**: The bot includes comprehensive error handling that sends error messages back to the user
- **Voice Service Logging**: Azure Speech Service operations are logged for debugging

#### Common Voice-Related Debug Messages

```bash
# Voice features working correctly
INFO: Bot initialized with voice capabilities enabled
INFO: Azure Speech Service initialized successfully
INFO: Voice live session started

# Voice features disabled (missing configuration)
WARNING: Bot initialized with voice capabilities disabled
WARNING: Azure Speech SDK not available. Voice features will be disabled.
WARNING: Speech-to-text not available: service not configured
```

### Common Development Tasks

```bash
# Install new dependencies
pip install <package-name>
pip freeze > requirements.txt  # Update requirements

# Format code (if using black formatter)
pip install black
black *.py

# Type checking (if using mypy)
pip install mypy
mypy *.py
```

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'azure.cognitiveservices.speech'

**Solution**: Install the Azure Speech Service SDK:
```bash
pip install azure-cognitiveservices-speech
```

#### Voice features not working / "Voice features are not available"

**Common causes and solutions**:
- **Missing Azure Speech Service configuration**: Set `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` environment variables
- **Invalid speech service credentials**: Verify your Azure Speech Service key and region in the Azure portal
- **Speech SDK not installed**: Run `pip install azure-cognitiveservices-speech`
- **Region mismatch**: Ensure the region matches your Azure Speech Service resource (e.g., "eastus", "westus2")

#### Speech-to-text not working with audio attachments

**Solution**: This requires additional implementation to download and process audio attachments. The current implementation shows placeholder functionality.

#### ModuleNotFoundError: No module named 'botbuilder'

**Solution**: Make sure you've installed the dependencies:
```bash
pip install -r requirements.txt
```

#### Port 3978 is already in use

**Solution**: Either stop the existing process or change the port:
```bash
# Option 1: Kill existing process (Windows)
netstat -ano | findstr :3978
taskkill /PID <PID> /F

# Option 1: Kill existing process (macOS/Linux)
lsof -ti:3978 | xargs kill -9

# Option 2: Use a different port
export PORT=3979  # or set in .env file
python app.py
```

#### Python version compatibility issues

**Solution**: Ensure you're using Python 3.6 or higher:
```bash
python --version
# If needed, use python3 explicitly
python3 app.py
```

#### Bot Framework Emulator connection issues

**Common causes and solutions**:
- **Wrong endpoint**: Make sure you're connecting to `http://localhost:3978/api/messages` (note the `/api/messages` path)
- **Bot not running**: Ensure the bot is running and showing the "Running on http://localhost:3978" message
- **Firewall/antivirus**: Check if local firewall or antivirus is blocking the connection

### Getting Help

If you encounter issues not covered here:

1. **Check the console output** for detailed error messages
2. **Review the Bot Framework documentation**: https://docs.microsoft.com/en-us/azure/bot-service/
3. **Check the issues** in this repository
4. **Create a new issue** with details about your problem and environment

## Project Structure

```
├── app.py              # Main application entry point and web server setup
├── bot.py              # AI-powered bot class with voice capabilities  
├── ai_agent_service.py # Azure AI Foundry integration for intelligent responses
├── voice_service.py    # Azure Speech Service integration and Voice Live Agent
├── config.py           # Configuration settings and environment variables
├── start_bot.py        # Alternative startup script with user-friendly output
├── test_bot.py         # Unit tests for bot functionality
├── requirements.txt    # Python dependencies including Azure AI and Speech Services
├── .gitignore         # Git ignore file
└── README.md          # This documentation file
```

### File Descriptions

- **`app.py`**: Sets up the aiohttp web server, Bot Framework adapter, and handles incoming HTTP requests
- **`bot.py`**: Contains the AI-powered bot class with voice capabilities, supporting both text and voice interactions with intelligent responses
- **`ai_agent_service.py`**: Implements Azure AI Foundry integration for generating intelligent responses instead of simple echoing
- **`voice_service.py`**: Implements Azure Speech Service integration including speech-to-text, text-to-speech, and Voice Live Agent functionality
- **`config.py`**: Manages configuration settings using environment variables with Azure AI Foundry and Speech Service settings
- **`start_bot.py`**: Alternative entry point that provides more user-friendly startup messages
- **`test_bot.py`**: Unit tests using Python's `unittest` framework to validate bot functionality

## How It Works

### AI-Powered Bot Framework Architecture

1. **HTTP Server** (`app.py`): Receives HTTP POST requests from Bot Framework channels
2. **Bot Framework Adapter**: Processes incoming activities and handles authentication
3. **AI-Powered Bot Logic** (`bot.py`): Implements bot behavior with AI agent and voice capabilities
4. **AI Agent Service** (`ai_agent_service.py`): Handles Azure AI Foundry integration for intelligent responses
5. **Voice Service** (`voice_service.py`): Handles Azure Speech Service integration
6. **Configuration** (`config.py`): Manages app settings, credentials, AI, and voice service configuration

### Message Flow

1. User sends a message (text or audio) through a channel (Bot Framework Emulator, Teams, etc.)
2. Bot Framework service forwards the message to your bot's endpoint (`/api/messages`)
3. The aiohttp server receives the HTTP request
4. Bot Framework Adapter deserializes the activity and calls the bot's message handler
5. AI-powered bot processes the message using Azure AI Foundry for intelligent responses
6. If voice session is active, response can be converted to speech using Azure Speech Service
7. Response is sent back through the same channel to the user

### AI Processing Flow

1. **User Input**: Text or speech input from user
2. **AI Agent Processing**: User message → Azure AI Foundry → Intelligent response
3. **Conversation History**: Maintains context across conversation turns
4. **Fallback Handling**: Graceful degradation when AI services are not configured

### Voice Processing Flow

1. **Speech-to-Text**: Audio input → Azure Speech Service → Recognized text
2. **AI Processing**: Recognized text → AI Agent → Intelligent response text  
3. **Text-to-Speech**: Response text → Azure Speech Service → Audio output
4. **Voice Live Agent**: Manages real-time voice interactions and session state

### Key Components

The AI-powered bot implements the `ActivityHandler` class and overrides:
- **`on_message_activity`**: Handles incoming text messages, voice commands, and audio attachments with AI responses
- **`on_members_added_activity`**: Welcomes new users and explains AI and voice capabilities

#### AI Agent Components

- **`AIAgentService`**: Core Azure AI Foundry integration for intelligent conversation responses
- **`ConversationHistory`**: Manages conversation context and history for better AI responses
- **Fallback Responses**: Provides helpful responses when AI services are not configured

#### Voice Service Components

- **`VoiceService`**: Core Azure Speech Service integration for speech-to-text and text-to-speech
- **`VoiceLiveAgent`**: Manages voice session state and real-time voice interactions
- **Voice Commands**: `/voice`, `/voices`, `/help` for controlling voice functionality

## Deployment

### Local Development vs Production

- **Local Development**: No credentials needed, uses empty `MicrosoftAppId` and `MicrosoftAppPassword`
- **Production**: Requires valid Azure Bot Service credentials

### Deploying to Azure

To deploy this bot to Azure Bot Service:

1. **Create Azure resources**:
   - Create an Azure Bot Service resource in the Azure portal
   - Create an Azure App Service or Container Instance for hosting

2. **Configure authentication**:
   - Set the `MicrosoftAppId` environment variable with your bot's Application ID
   - Set the `MicrosoftAppPassword` environment variable with your bot's client secret

3. **Deploy the code**:
   - Deploy to Azure App Service using Git, VS Code, or Azure CLI
   - Or containerize and deploy to Azure Container Instances

4. **Update Bot configuration**:
   - In the Azure portal, update your bot's messaging endpoint to point to your deployed app
   - Test the bot in the Web Chat or other configured channels

### Environment Variables for Production

```bash
# Required for Azure deployment
MicrosoftAppId=your-bot-app-id
MicrosoftAppPassword=your-bot-client-secret
PORT=80  # or the port your hosting service expects

# Required for AI features in production
AZURE_AI_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_AI_API_KEY=your-azure-ai-api-key
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Required for voice features in production
AZURE_SPEECH_KEY=your-azure-speech-service-key  
AZURE_SPEECH_REGION=your-azure-speech-region

# Optional for advanced voice features
AZURE_VOICE_LIVE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VOICE_LIVE_KEY=your-voice-live-key
```

## Voice Live API Implementation

This bot implements the Azure Speech Service Voice Live API following Microsoft's official documentation. Key features include:

### Speech-to-Text Capabilities
- Real-time speech recognition using Azure Speech Service
- Support for multiple languages (configured for en-US by default)
- Error handling and fallback for recognition failures

### Text-to-Speech Capabilities  
- Neural voice synthesis using Azure Speech Service
- Multiple voice options (default: en-US-JennyNeural)
- Audio output in WAV format for bot responses

### Voice Live Agent Features
- Session management for voice interactions
- Real-time processing of voice inputs
- Integration with bot conversation flow

### Voice Commands
- `/voice` - Start voice session for enhanced voice interactions
- `/voices` - List available neural voices from Azure Speech Service  
- `/help` - Display all available commands and voice status

### Setup Requirements for Voice Features

1. **Azure Speech Service Resource**:
   ```bash
   # Create in Azure Portal or using Azure CLI
   az cognitiveservices account create \
     --name "your-speech-service" \
     --resource-group "your-resource-group" \
     --kind "SpeechServices" \
     --sku "S0" \
     --location "eastus"
   ```

2. **Environment Configuration**:
   ```bash
   export AZURE_SPEECH_KEY="your_key_here"
   export AZURE_SPEECH_REGION="eastus"
   ```

3. **Install Dependencies**:
   ```bash
   pip install azure-ai-inference azure-identity azure-cognitiveservices-speech>=1.24.0
   ```

The implementation gracefully handles cases where AI or voice services are not configured, allowing the bot to provide fallback responses when services are unavailable.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python test_bot.py`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project follows the Microsoft Bot Framework licensing terms. The Bot Framework SDK is licensed under the MIT License.

## Additional Resources

- [Bot Framework Documentation](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Python Bot Framework SDK](https://github.com/Microsoft/botbuilder-python)
- [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator)
- [Azure Bot Service](https://azure.microsoft.com/en-us/services/bot-service/)
- [Bot Framework Samples](https://github.com/Microsoft/BotBuilder-Samples)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Foundry Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?tabs=python&pivots=fdp-project)
- [Azure Speech Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/)
- [Voice Live Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live-agents-quickstart?tabs=windows%2Ckeyless&pivots=programming-language-python)
- [Azure AI Foundry Portal](https://ai.azure.com/)