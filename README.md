# Bot Framework Python Echo Bot

This repository contains a simple Echo Bot built using the Microsoft Bot Framework SDK for Python, following the [official Microsoft quickstart guide](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-create-bot?view=azure-bot-service-4.0&tabs=python%2Cvs).

## Features

- **Echo Bot**: Responds to user messages by echoing them back with "Echo: " prefix
- **Welcome Message**: Greets new users when they join the conversation
- **Error Handling**: Comprehensive error handling with debugging support
- **Bot Framework Integration**: Uses the official Microsoft Bot Framework SDK

## Prerequisites

- Python 3.6 or higher
- pip package manager

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Kami-python-test
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Bot

1. Start the bot application:
   ```bash
   python app.py
   ```

2. The bot will start running on `http://localhost:3978`

3. You should see the message:
   ```
   ======== Running on http://localhost:3978 ========
   (Press CTRL+C to quit)
   ```

## Testing the Bot

### Using Bot Framework Emulator

1. Download and install the [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
2. Start the bot using `python app.py`
3. Open Bot Framework Emulator
4. Connect to `http://localhost:3978/api/messages`
5. Start chatting with your bot!

### Using ngrok (for external testing)

1. Install [ngrok](https://ngrok.com/)
2. Start the bot: `python app.py`
3. In another terminal, run: `ngrok http 3978`
4. Use the ngrok URL for external testing

## Project Structure

```
├── app.py              # Main application entry point
├── bot.py              # EchoBot class implementation
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Configuration

The bot uses environment variables for configuration:

- `MicrosoftAppId`: Bot application ID (leave empty for local testing)
- `MicrosoftAppPassword`: Bot application password (leave empty for local testing)
- `PORT`: Server port (defaults to 3978)

## How It Works

1. **app.py**: Sets up the web server and Bot Framework adapter
2. **bot.py**: Contains the EchoBot class that handles incoming messages
3. **config.py**: Manages configuration settings and environment variables

The bot implements the `ActivityHandler` class and overrides:
- `on_message_activity`: Handles incoming text messages
- `on_members_added_activity`: Welcomes new users

## Deployment

To deploy this bot to Azure:

1. Create an Azure Bot Service resource
2. Set the `MicrosoftAppId` and `MicrosoftAppPassword` environment variables
3. Deploy the code to Azure App Service or Azure Container Instances
4. Update the messaging endpoint in the Azure portal

## License

This project follows the Microsoft Bot Framework licensing terms.