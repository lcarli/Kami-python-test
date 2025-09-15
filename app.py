#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from aiohttp_cors import setup as setup_cors, ResourceOptions
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from bot import EchoBot
from config import DefaultConfig

CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Try to send a message to the user, but handle service_url issues
    try:
        if context.activity.service_url:
            await context.send_activity("The bot encountered an error or bug.")
            await context.send_activity(
                "To continue to run this bot, please fix the bot source code."
            )
        else:
            print("Cannot send error message - service_url is None (likely web client)")
    except Exception as send_error:
        print(f"Could not send error message: {send_error}")
    
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        try:
            # Create a trace activity that contains the error object
            trace_activity = Activity(
                label="TurnError",
                name="on_turn_error Trace",
                timestamp=datetime.now(datetime.UTC),
                type=ActivityTypes.trace,
                value=f"{error}",
                value_type="https://www.botframework.com/schemas/error",
            )
            # Send a trace activity, which will be displayed in Bot Framework Emulator
            await context.send_activity(trace_activity)
        except Exception as trace_error:
            print(f"Could not send trace activity: {trace_error}")


ADAPTER.on_turn_error = on_error

# Create the Bot
BOT = EchoBot()


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


# Custom endpoint for web client that bypasses Bot Framework limitations
async def web_chat(req: Request) -> Response:
    """Handle direct messages from web client without Bot Framework constraints."""
    try:
        if "application/json" not in req.headers.get("Content-Type", ""):
            return Response(status=415)

        body = await req.json()
        user_message = body.get("text", "").strip()
        
        if not user_message:
            return json_response({"error": "No message provided"}, status=400)
        
        # Get AI response directly using the bot's AI service
        try:
            if BOT.ai_agent_service.is_available():
                ai_response = await BOT.ai_agent_service.get_response(user_message)
            else:
                ai_response = await BOT.ai_agent_service.get_fallback_response(user_message)
            
            if ai_response:
                return json_response({
                    "type": "message",
                    "text": ai_response,
                    "timestamp": datetime.now(datetime.UTC).isoformat(),
                    "from": {"id": "bot", "name": "Kami Bot"}
                })
            else:
                return json_response({
                    "type": "message", 
                    "text": "I'm sorry, I couldn't generate a response at the moment. Please try again.",
                    "timestamp": datetime.now(datetime.UTC).isoformat(),
                    "from": {"id": "bot", "name": "Kami Bot"}
                })
                
        except Exception as e:
            print(f"Error in web chat AI processing: {e}")
            return json_response({
                "type": "message",
                "text": "I encountered an error while processing your message. Please try again.",
                "timestamp": datetime.now(datetime.UTC).isoformat(),
                "from": {"id": "bot", "name": "Kami Bot"}
            })
            
    except Exception as e:
        print(f"Error in web chat endpoint: {e}")
        return json_response({"error": "Internal server error"}, status=500)


def init_func(argv):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    
    # Setup CORS for web client access
    cors = setup_cors(APP, defaults={
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    messages_route = APP.router.add_post("/api/messages", messages)
    web_chat_route = APP.router.add_post("/api/webchat", web_chat)
    
    # Add CORS to the routes
    cors.add(messages_route)
    cors.add(web_chat_route)
    
    return APP


if __name__ == "__main__":
    APP = init_func(None)

    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error