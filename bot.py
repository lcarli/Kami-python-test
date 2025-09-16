#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
from typing import Optional

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes

from ai_agent_service import AIAgentService, ConversationHistory
from config import DefaultConfig


class KamiBot(ActivityHandler):
    """
    Enhanced bot with AI agent capabilities using Azure AI Foundry.
    This bot will respond using AI agent intelligence instead of simple echoing.
    """

    def __init__(self):
        self.config = DefaultConfig()
        self.ai_agent_service = AIAgentService(self.config)
        self.conversation_history = ConversationHistory()
        
        # Log service availability
        if self.ai_agent_service.is_available():
            logging.info("Bot initialized with AI agent capabilities enabled")
        else:
            logging.warning("Bot initialized with AI agent capabilities disabled - using fallback responses")

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        """Welcome new members and explain AI agent capabilities."""
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                welcome_message = "Hello and welcome! I'm an AI assistant bot."
                
                if self.ai_agent_service.is_available():
                    welcome_message += " I can have intelligent conversations using Azure AI Foundry."
                else:
                    welcome_message += " AI features are currently unavailable, but I can still chat with you!"
                
                welcome_message += " You can type messages to chat with me."
                
                await turn_context.send_activity(welcome_message)

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle text messages with AI agent responses."""
        activity = turn_context.activity
        
        # Handle text commands and messages
        user_text = activity.text.strip() if activity.text else ""
        
        if user_text.lower() == '/help':
            return await self._handle_help_command(turn_context)
        else:
            # Use AI agent for intelligent responses instead of echo
            return await self._handle_ai_response(turn_context, user_text)

    async def _handle_help_command(self, turn_context: TurnContext) -> None:
        """Handle the /help command to show available features."""
        help_message = "🤖 AI Assistant Bot Help\n\n"
        
        if self.ai_agent_service.is_available():
            help_message += "✅ AI Agent Features Available:\n"
            help_message += "- Intelligent conversations using Azure AI Foundry\n"
            help_message += "- Context-aware responses\n"
            help_message += "- Natural language understanding\n\n"
        else:
            help_message += "❌ AI Agent Features Unavailable:\n"
            help_message += "- Please configure Azure AI Foundry credentials\n\n"
        
        help_message += "📝 Available Commands:\n"
        help_message += "- /help - Show this help message\n"
        help_message += "- Any text message - Get AI-powered responses\n\n"
        help_message += "💡 Just type any message and I'll respond intelligently!"
        
        await turn_context.send_activity(help_message)

    async def _safe_send_activity(self, turn_context: TurnContext, message: str) -> bool:
        """Safely send an activity, handling service_url issues."""
        try:
            # Check if we have a valid service URL
            if not turn_context.activity.service_url:
                logging.warning("service_url is None, cannot send response via Bot Framework")
                return False
            
            await turn_context.send_activity(message)
            return True
        except Exception as e:
            logging.error(f"Error sending activity: {e}")
            return False

    async def _handle_ai_response(self, turn_context: TurnContext, user_text: str) -> None:
        """Handle user messages with AI agent responses."""
        try:
            # Add user message to conversation history
            self.conversation_history.add_user_message(user_text)
            
            # Get AI response
            if self.ai_agent_service.is_available():
                ai_response = await self.ai_agent_service.get_response(
                    user_text, 
                    self.conversation_history.get_history()
                )
            else:
                ai_response = await self.ai_agent_service.get_fallback_response(user_text)
            
            if ai_response:
                # Add AI response to conversation history
                self.conversation_history.add_assistant_message(ai_response)
                
                # Send text response
                success = await self._safe_send_activity(turn_context, ai_response)
                
                if not success:
                    logging.info("Response generated but couldn't send via Bot Framework - likely web client")
            else:
                await self._safe_send_activity(
                    turn_context,
                    "I'm sorry, I couldn't generate a response at the moment. Please try again."
                )
                
        except Exception as e:
            logging.error(f"Error handling AI response: {e}")
            await self._safe_send_activity(
                turn_context,
                "I encountered an error while processing your message. Please try again."
            )