#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
from typing import Optional

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes

from voice_service import VoiceService, VoiceLiveAgent
from ai_agent_service import AIAgentService, ConversationHistory
from config import DefaultConfig


class EchoBot(ActivityHandler):
    """
    Enhanced bot with AI agent capabilities using Azure AI Foundry and voice features.
    This bot will respond using AI agent intelligence instead of simple echoing.
    """

    def __init__(self):
        self.config = DefaultConfig()
        self.voice_service = VoiceService(self.config)
        self.voice_agent = VoiceLiveAgent(self.voice_service)
        self.ai_agent_service = AIAgentService(self.config)
        self.conversation_history = ConversationHistory()
        
        # Log service availability
        if self.ai_agent_service.is_available():
            logging.info("Bot initialized with AI agent capabilities enabled")
        else:
            logging.warning("Bot initialized with AI agent capabilities disabled - using fallback responses")
            
        if self.voice_service.is_available():
            logging.info("Bot initialized with voice capabilities enabled")
        else:
            logging.warning("Bot initialized with voice capabilities disabled")

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        """Welcome new members and explain AI agent and voice capabilities."""
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                welcome_message = "Hello and welcome! I'm an AI assistant bot with voice capabilities."
                
                if self.ai_agent_service.is_available():
                    welcome_message += "\n\n🤖 AI agent features enabled - I can provide intelligent responses to your questions!"
                else:
                    welcome_message += "\n\n⚠️ AI agent features are disabled. Please configure Azure AI Foundry to enable intelligent responses."
                
                if self.voice_service.is_available():
                    welcome_message += "\n\n🎤 Voice features available:"
                    welcome_message += "\n- Send audio messages and I'll transcribe them"
                    welcome_message += "\n- Type '/voice' to enable voice responses"
                    welcome_message += "\n- Type '/voices' to see available voice options"
                else:
                    welcome_message += "\n\n🔇 Voice features are currently disabled. Please configure Azure Speech Service to enable them."
                
                welcome_message += "\n\nType '/help' for more information!"
                await turn_context.send_activity(welcome_message)

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle both text and voice messages with AI agent responses."""
        activity = turn_context.activity
        
        # Handle voice/audio attachments
        if activity.attachments:
            for attachment in activity.attachments:
                if attachment.content_type and 'audio' in attachment.content_type:
                    return await self._handle_audio_message(turn_context, attachment)
        
        # Handle text commands and messages
        user_text = activity.text.strip() if activity.text else ""
        
        if user_text.lower() == '/voice':
            return await self._handle_voice_command(turn_context)
        elif user_text.lower() == '/voices':
            return await self._handle_voices_command(turn_context)
        elif user_text.lower() == '/help':
            return await self._handle_help_command(turn_context)
        else:
            # Use AI agent for intelligent responses instead of echo
            return await self._handle_ai_response(turn_context, user_text)

    async def _handle_audio_message(self, turn_context: TurnContext, attachment) -> None:
        """Handle incoming audio messages with AI agent responses."""
        if not self.voice_service.is_available():
            await turn_context.send_activity(
                "Voice features are not available. Please configure Azure Speech Service."
            )
            return
        
        try:
            # In a real implementation, you would download the audio attachment
            # and process it with speech-to-text, then use AI agent for response
            await turn_context.send_activity(
                "🎤 I received an audio message! Voice processing is configured and would:"
                "\n1. Convert your speech to text using Azure Speech Service"
                "\n2. Generate an intelligent response using AI agent"
                "\n3. Convert the response back to speech if voice session is active"
                "\n\nFull audio processing requires additional implementation to download and process the audio attachment."
            )
            
        except Exception as e:
            logging.error(f"Error processing audio message: {e}")
            await turn_context.send_activity(
                "Sorry, I encountered an error while processing your audio message."
            )

    async def _handle_voice_command(self, turn_context: TurnContext) -> None:
        """Handle the /voice command to enable voice responses."""
        if not self.voice_service.is_available():
            await turn_context.send_activity(
                "Voice features are not available. Please configure Azure Speech Service with:"
                "\n- AZURE_SPEECH_KEY environment variable"
                "\n- AZURE_SPEECH_REGION environment variable"
            )
            return
        
        try:
            await self.voice_agent.start_voice_session()
            await turn_context.send_activity(
                "Voice session started! I can now process voice inputs and provide voice responses. "
                "Send me text and I'll respond with voice when possible."
            )
            
        except Exception as e:
            logging.error(f"Error starting voice session: {e}")
            await turn_context.send_activity(
                "Sorry, I couldn't start the voice session. Please check the Azure Speech Service configuration."
            )

    async def _handle_voices_command(self, turn_context: TurnContext) -> None:
        """Handle the /voices command to show available voices."""
        if not self.voice_service.is_available():
            await turn_context.send_activity(
                "Voice features are not available. Please configure Azure Speech Service."
            )
            return
        
        try:
            voices = self.voice_service.get_supported_voices()
            
            if voices:
                voice_list = "Available voices:\n"
                # Show first 5 voices as examples
                for voice in voices[:5]:
                    voice_list += f"- {voice['display_name']} ({voice['locale']}, {voice['gender']})\n"
                
                if len(voices) > 5:
                    voice_list += f"\n... and {len(voices) - 5} more voices available."
                
                await turn_context.send_activity(voice_list)
            else:
                await turn_context.send_activity("No voices are currently available.")
                
        except Exception as e:
            logging.error(f"Error getting voices: {e}")
            await turn_context.send_activity(
                "Sorry, I couldn't retrieve the available voices."
            )

    async def _handle_help_command(self, turn_context: TurnContext) -> None:
        """Handle the /help command."""
        help_text = "Available commands:\n"
        help_text += "- Type any text to get an AI-powered response\n"
        help_text += "- Send audio messages for voice processing (if configured)\n"
        help_text += "- /voice - Enable voice session\n"
        help_text += "- /voices - List available voices\n"
        help_text += "- /help - Show this help message\n"
        
        if self.ai_agent_service.is_available():
            help_text += "\n🤖 AI agent features are enabled!"
        else:
            help_text += "\n⚠️ AI agent features are disabled. Configure Azure AI Foundry to enable intelligent responses."
        
        if self.voice_service.is_available():
            help_text += "\n🎤 Voice features are enabled!"
        else:
            help_text += "\n🔇 Voice features are disabled. Configure Azure Speech Service to enable them."
        
        await turn_context.send_activity(help_text)

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
                
                # Check if voice session is active and provide voice response
                if (self.voice_agent.is_active and 
                    self.voice_service.is_available()):
                    
                    # Generate voice response
                    voice_audio = await self.voice_service.text_to_speech(ai_response)
                    if voice_audio:
                        # In a real implementation, you would send the audio back to the user
                        # For now, we'll just send the text with a note about voice
                        await turn_context.send_activity(
                            f"🔊 {ai_response}\n\n(Voice response generated but audio delivery requires additional implementation)"
                        )
                    else:
                        await turn_context.send_activity(ai_response)
                else:
                    await turn_context.send_activity(ai_response)
            else:
                await turn_context.send_activity(
                    "I'm sorry, I couldn't generate a response at the moment. Please try again."
                )
                
        except Exception as e:
            logging.error(f"Error handling AI response: {e}")
            await turn_context.send_activity(
                "I encountered an error while processing your message. Please try again."
            )