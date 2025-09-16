# KA## ✨ Features

- **🎯 Wake Word Detection**: Automatically activates voice conversation when you say "Hey, Kami"
- **🤖 AI-Powered**: Intelligent responses using Azure AI Foundry agent
- **🎤 Always-On Voice**: Voice Live conversation ready from startup
- **💬 Unified Interface**: Type messages or speak naturally with wake word
- **🔇 Smart Microphone Control**: Mute/unmute microphone with visual indicators
- **🌐 Modern Web Interface**: Clean, responsive browser-based interface
- **⚡ Auto-Start**: Voice conversation active immediately on launch
- **🛡️ Secure**: Environment-based Azure credential managementI Voice Assistant with Wake Word Detection

KAMI (Knowledge and Azure Multilingual Intelligence) is an AI-powered voice assistant that combines intelligent text chat with automatic voice activation through wake word detection. Built with Azure AI Foundry and Azure Voice Live API, KAMI provides a seamless hands-free conversation experience that activates when you say "Hey, Kami".

## ✨ Features

- **� AI-Powered**: Intelligent responses using Azure AI Foundry agent
- **�️ Hybrid Interface**: Seamless switching between text and voice conversation
- **�️ Voice Live API**: Real-time voice conversation with Azure Voice Live
- **💬 Text Chat**: Traditional text-based conversation interface
- **🔄 Unified Experience**: Single interface for both text and voice interactions
- **🌐 Web Interface**: Modern browser-based hybrid interface
- **⚡ One-Click Launch**: Single command starts everything
- **🛡️ Secure**: Environment-based Azure credential management

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Kami-python-test
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your Azure credentials:
```env
# Azure AI Foundry (Required for intelligent responses)
AI_FOUNDRY_AGENT_ID=your_agent_id
AI_FOUNDRY_PROJECT_NAME=your_project_name
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=your_tenant_id

# Azure Voice Live API (Required for voice conversation)
AZURE_VOICE_LIVE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VOICE_LIVE_KEY=your_voice_live_key
```

### 3. Launch KAMI
```bash
python hybrid_bot.py
```

### 4. Start Conversing
- Browser opens to: `http://localhost:3978`
- **Voice is automatically active** - just say "Hey, Kami" to talk
- **Type messages** anytime for text chat
- **Use microphone button** to mute/unmute when needed
- Enjoy hands-free AI conversations!

## 📋 Prerequisites

- **Python 3.8+** - `python --version`
- **pip** - Package manager
- **Azure AI Foundry** - For intelligent AI agent responses
- **Azure Voice Live API** - For real-time voice conversation
- **Modern web browser** - Chrome/Edge recommended for best experience

## ⚙️ Azure Setup

### Azure AI Foundry (Required for AI responses)
1. Visit [Azure AI Foundry](https://ai.azure.com/)
2. Create or access your AI hub and project
3. Create an AI agent (assistant) in your project
4. Copy the **Agent ID** (starts with "asst_")
5. Copy the **Project Name**
6. Create service principal credentials for authentication

### Azure Voice Live API (Required for voice conversation)
1. Create an **Azure Voice Live** resource in Azure Portal
2. Copy the **Endpoint URL** and **API Key**
3. Ensure Voice Live is configured for your AI Foundry project

### Setting up Azure Credentials
1. Create an **App Registration** in Azure AD
2. Copy the **Client ID**, **Client Secret**, and **Tenant ID**
3. Grant appropriate permissions to access AI Foundry and Voice Live services

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

The hybrid bot uses environment variables for Azure service configuration. All features require proper Azure AI Foundry and Voice Live API setup.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AI_FOUNDRY_AGENT_ID` | Azure AI Foundry agent ID (starts with "asst_") | **Yes** |
| `AI_FOUNDRY_PROJECT_NAME` | Azure AI Foundry project name | **Yes** |
| `AZURE_CLIENT_ID` | Azure service principal client ID | **Yes** |
| `AZURE_CLIENT_SECRET` | Azure service principal client secret | **Yes** |
| `AZURE_TENANT_ID` | Azure tenant ID | **Yes** |
| `AZURE_VOICE_LIVE_ENDPOINT` | Azure Voice Live API endpoint | **Yes** |
| `AZURE_VOICE_LIVE_KEY` | Azure Voice Live API key | **Yes** |
| `PORT` | Server port | No (default: 3978) |

### Complete .env File Example

Create a `.env` file in the project root:

```bash
# Azure AI Foundry Configuration
AI_FOUNDRY_AGENT_ID=asst_R0j0hoILsRKk7BSRKQhF9IrE
AI_FOUNDRY_PROJECT_NAME=KamiProject

# Azure Authentication
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_TENANT_ID=your-tenant-id-here

# Azure Voice Live API
AZURE_VOICE_LIVE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VOICE_LIVE_KEY=your-voice-live-key-here

# Optional: Server Configuration
PORT=3978
```

## Running KAMI Bot

### Using the direct launch (recommended)

```bash
python hybrid_bot.py
```

The bot will automatically:
- Start the KAMI server on port 3978
- Initialize wake word detection for "Hey, Kami"
- Start Voice Live conversation automatically
- Open browser to the KAMI interface
- Display service status and features

### Expected Output

When KAMI starts successfully, you should see:

```
[HYBRID] Starting Kami Hybrid Bot on port 3978
   [WEB] Interface: http://localhost:3978
   [CHAT] Text & Voice: http://localhost:3978/hybrid
   [INFO] Press Ctrl+C to stop
```

Browser opens automatically to KAMI interface with:
- Wake word detection active and listening for "Hey, Kami"
- Voice Live conversation ready
- Text input available anytime
- Microphone controls visible in header

## Using KAMI Interface

### Wake Word Voice Activation
1. **Say "Hey, Kami"** to automatically start voice conversation
2. **Speak naturally** - your voice is processed in real-time
3. **Listen to AI responses** through voice synthesis
4. **Continue talking** or return to text input

### Text Chat
1. **Type messages** in the chat input field anytime
2. **Press Enter** or click Send to send messages
3. **Receive AI responses** from your Azure AI Foundry agent
4. **View conversation history** in the chat area

### Microphone Control
1. **Microphone is active by default** for wake word detection
2. **Click microphone button** in header to mute/unmute
3. **Visual indicators** show microphone and wake word status
4. **Green pulsing dot** = listening for "Hey, Kami"
5. **Red indicator** = microphone muted

### Unified Experience
- Voice conversation starts automatically when KAMI loads
- Wake word detection runs continuously in background
- Type messages anytime while wake word detection is active
- Same Azure AI Foundry agent handles both text and voice
- Conversation context preserved across interaction types

## Testing KAMI Bot

### Testing Wake Word Detection
1. **Start KAMI**: `python hybrid_bot.py`
2. **Open browser** to `http://localhost:3978`
3. **Grant microphone permissions** when prompted by browser
4. **Say "Hey, Kami"** and verify voice conversation starts
5. **Check wake word indicator** shows "triggered" state

### Testing Text Chat
1. **Type messages** in the chat input field
2. **Press Enter** to send messages
3. **Verify AI responses** from Azure AI Foundry agent
4. **Test while wake word is active** to ensure both work together

### Testing Voice Conversation
1. **Say "Hey, Kami"** to activate voice conversation
2. **Speak naturally** to test real-time voice processing
3. **Verify voice responses** from Azure Voice Live API
4. **Check console output** for Voice Live service status

### Testing Microphone Controls
1. **Click microphone button** in header to mute
2. **Verify wake word indicator** shows "muted" state
3. **Test that wake word detection stops** when muted
4. **Click microphone button again** to unmute and resume

### Testing Environment Configuration
KAMI will display configuration status on startup:
- AI Foundry agent connection status
- Voice Live API availability
- Required environment variables validation
- Wake word detection initialization

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
├── hybrid_bot.py       # Main KAMI interface with wake word detection and auto-start voice
├── ai_agent_service.py # Azure AI Foundry agent integration
├── bot.py              # Core bot logic and conversation handling
├── config.py           # Configuration settings and environment variables
├── static/             # Web interface files
│   ├── index.html      # KAMI web interface with wake word controls
│   ├── styles.css      # Modern responsive styling
│   └── script.js       # Wake word detection and voice/text integration
├── requirements.txt    # Python dependencies
├── prompt_kami.md      # AI agent prompt configuration
├── .gitignore         # Git ignore file
└── README.md          # This documentation file
```

### File Descriptions

- **`hybrid_bot.py`**: Main KAMI application with wake word detection, auto-start voice conversation, and unified text/voice interface
- **`ai_agent_service.py`**: Handles Azure AI Foundry agent communication for intelligent responses in both text and voice interactions
- **`bot.py`**: Core bot framework logic supporting conversation management and message processing
- **`config.py`**: Manages all configuration settings including Azure credentials and service endpoints
- **`static/`**: Web interface files for KAMI's browser-based interface
  - **`index.html`**: Main web interface with wake word indicators and microphone controls
  - **`styles.css`**: Modern, clean styling with responsive design
  - **`script.js`**: JavaScript handling wake word detection, voice activation, and text chat
- **`prompt_kami.md`**: Contains the AI agent personality and behavior configuration

## How It Works

### Wake Word Detection Architecture

KAMI uses an always-on voice architecture with intelligent wake word detection:

1. **Auto-Start Voice Live**: Voice conversation activates automatically when KAMI loads
2. **Continuous Wake Word Listening**: Browser-based speech recognition listens for "Hey, Kami"
3. **Instant Voice Activation**: Speaking the wake word immediately triggers voice conversation
4. **Unified AI Agent**: Same Azure AI Foundry agent handles both text and voice interactions
5. **Smart Microphone Control**: Visual indicators and mute controls for user privacy

### Message Flow

#### Text Chat Flow
1. User types message in web interface
2. Message sent to KAMI server
3. AI Agent Service processes message through Azure AI Foundry
4. Intelligent response returned to web interface
5. Response displayed in chat area

#### Wake Word Voice Flow
1. User says "Hey, Kami" (wake word detected by browser)
2. Voice conversation automatically activates
3. User speaks - voice captured and sent to Voice Live service
4. Azure Voice Live API processes speech in real-time
5. Voice Live service forwards to Azure AI Foundry agent
6. AI agent generates response
7. Response synthesized to speech and played back

### AI Processing

Both text and voice use the same Azure AI Foundry agent:
- **Agent ID**: Configured in environment variables
- **Project Integration**: Connected to Azure AI Foundry project
- **Context Preservation**: Conversation history maintained across interaction types
- **Intelligent Responses**: Powered by Azure AI Foundry's advanced language models  
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

## Troubleshooting

### Common Issues

#### Wake word detection not working

**Common causes and solutions**:
- **Browser microphone permissions**: Grant microphone access when prompted by browser
- **Speech recognition not supported**: Wake word detection requires modern browsers (Chrome/Edge recommended)
- **Microphone muted**: Check that microphone button in header is not muted (should show green pulsing dot)
- **Language settings**: Wake word detection is configured for Portuguese ("Hey, Kami", "Ei, Kami", "Oi, Kami")
- **Background noise**: Ensure clear speech in quiet environment for better detection

#### Voice Live not working / "Voice features are not available"

**Common causes and solutions**:
- **Missing Azure Voice Live configuration**: Set `AZURE_VOICE_LIVE_ENDPOINT` and `AZURE_VOICE_LIVE_KEY` environment variables
- **Invalid Voice Live credentials**: Verify your Azure Voice Live API key and endpoint in the Azure portal
- **AI Foundry agent not configured**: Ensure `AI_FOUNDRY_AGENT_ID` and `AI_FOUNDRY_PROJECT_NAME` are set correctly
- **Azure authentication issues**: Verify `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID` are correct

#### "No module named" errors

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
python start_all.py
```

#### Browser microphone permissions

**Solution**: 
- Grant microphone permissions when prompted by the browser for wake word detection and Voice Live functionality
- If permissions were denied, click the microphone icon in browser address bar to enable
- For Chrome: Settings > Privacy and security > Site Settings > Microphone
- For Edge: Settings > Site permissions > Microphone

#### KAMI interface not loading

**Common causes and solutions**:
- **Bot not running**: Ensure KAMI shows startup messages and "Press Ctrl+C to stop"
- **Wrong URL**: Access `http://localhost:3978` (main interface, not `/hybrid`)
- **Browser cache**: Try refreshing the page or clearing browser cache
- **JavaScript disabled**: Ensure JavaScript is enabled for wake word detection to work

### Getting Help

If you encounter issues not covered here:

1. **Check the console output** for detailed error messages
2. **Review the Azure AI Foundry documentation**: https://learn.microsoft.com/en-us/azure/ai-foundry/
3. **Check the issues** in this repository
4. **Create a new issue** with details about your problem and environment

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test the hybrid interface thoroughly
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project follows the MIT License.

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Foundry Portal](https://ai.azure.com/)
- [Azure Voice Live API Documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live-agents-quickstart)
- [Azure AI Services Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)
- [Azure Authentication Documentation](https://learn.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate)