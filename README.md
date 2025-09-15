# Bot Framework Python Echo Bot

This repository contains a simple Echo Bot built using the Microsoft Bot Framework SDK for Python, following the [official Microsoft quickstart guide](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-create-bot?view=azure-bot-service-4.0&tabs=python%2Cvs).

## Features

- **Echo Bot**: Responds to user messages by echoing them back with "Echo: " prefix
- **Welcome Message**: Greets new users when they join the conversation
- **Error Handling**: Comprehensive error handling with debugging support
- **Bot Framework Integration**: Uses the official Microsoft Bot Framework SDK

## Prerequisites

Before setting up the bot locally, ensure you have:

- **Python 3.6 or higher** - Check with `python --version` or `python3 --version`
- **pip package manager** - Usually comes with Python, check with `pip --version`
- **Git** - For cloning the repository
- **Bot Framework Emulator** (optional) - For testing the bot locally

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

The bot uses environment variables for configuration. For local development, you typically don't need to set these.

### Environment Variables

| Variable | Description | Default | Required for Local |
|----------|-------------|---------|-------------------|
| `MicrosoftAppId` | Bot application ID from Azure | `""` (empty) | No |
| `MicrosoftAppPassword` | Bot application password from Azure | `""` (empty) | No |
| `PORT` | Server port | `3978` | No |

### Local Development Configuration

For local testing, you can run the bot without setting any environment variables. The bot will use default settings defined in `config.py`.

If you need to customize settings, create a `.env` file (not tracked by git):

```bash
# .env file (optional for local development)
MicrosoftAppId=
MicrosoftAppPassword=
PORT=3978
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

### Testing with Bot Framework Emulator

1. **Download and install** the [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. **Start the bot** using one of the methods above
3. **Open Bot Framework Emulator**
4. **Connect to** `http://localhost:3978/api/messages`
5. **Start chatting** with your bot!

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

- **Console Output**: The bot logs information to the console, including errors
- **Bot Framework Emulator**: Shows detailed conversation flow and errors
- **Error Handling**: The bot includes comprehensive error handling that sends error messages back to the user

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
├── bot.py              # EchoBot class implementation with message handling
├── config.py           # Configuration settings and environment variables
├── start_bot.py        # Alternative startup script with user-friendly output
├── test_bot.py         # Unit tests for bot functionality
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This documentation file
```

### File Descriptions

- **`app.py`**: Sets up the aiohttp web server, Bot Framework adapter, and handles incoming HTTP requests
- **`bot.py`**: Contains the `EchoBot` class that inherits from `ActivityHandler` and implements message processing logic
- **`config.py`**: Manages configuration settings using environment variables with sensible defaults
- **`start_bot.py`**: Alternative entry point that provides more user-friendly startup messages
- **`test_bot.py`**: Unit tests using Python's `unittest` framework to validate bot functionality

## How It Works

### Bot Framework Architecture

1. **HTTP Server** (`app.py`): Receives HTTP POST requests from Bot Framework channels
2. **Bot Framework Adapter**: Processes incoming activities and handles authentication
3. **Bot Logic** (`bot.py`): Implements the actual bot behavior and responses
4. **Configuration** (`config.py`): Manages app settings and credentials

### Message Flow

1. User sends a message through a channel (Bot Framework Emulator, Teams, etc.)
2. Bot Framework service forwards the message to your bot's endpoint (`/api/messages`)
3. The aiohttp server receives the HTTP request
4. Bot Framework Adapter deserializes the activity and calls the bot's message handler
5. EchoBot processes the message and sends a response
6. Response is sent back through the same channel to the user

### Key Components

The bot implements the `ActivityHandler` class and overrides:
- **`on_message_activity`**: Handles incoming text messages and returns echo responses
- **`on_members_added_activity`**: Welcomes new users when they join the conversation

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
```

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