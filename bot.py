#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
from typing import Optional

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes

from voice_service import VoiceService, VoiceLiveAgent
from config import DefaultConfig


class EchoBot(ActivityHandler):
    """
    Enhanced bot with voice capabilities using Azure Speech Service.
    This bot will respond to both text and voice inputs.
    """

    def __init__(self):
        self.config = DefaultConfig()
        self.voice_service = VoiceService(self.config)
        self.voice_agent = VoiceLiveAgent(self.voice_service)
        
        # Log voice service availability
        if self.voice_service.is_available():
            logging.info("Bot initialized with voice capabilities enabled")
        else:
            logging.warning("Bot initialized with voice capabilities disabled")

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        """Welcome new members and explain voice capabilities."""
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                welcome_message = "Hello and welcome! I'm an enhanced echo bot with voice capabilities."
                
                if self.voice_service.is_available():
                    welcome_message += "\n\nVoice features available:"
                    welcome_message += "\n- Send audio messages and I'll transcribe them"
                    welcome_message += "\n- Type '/voice' to enable voice responses"
                    welcome_message += "\n- Type '/voices' to see available voice options"
                else:
                    welcome_message += "\n\nVoice features are currently disabled. Please configure Azure Speech Service to enable them."
                
                await turn_context.send_activity(welcome_message)

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle both text and voice messages."""
        activity = turn_context.activity
        
        # Handle voice/audio attachments
        if activity.attachments:
            for attachment in activity.attachments:
                if attachment.content_type and 'audio' in attachment.content_type:
                    return await self._handle_audio_message(turn_context, attachment)
        
        # Handle text commands
        user_text = activity.text.strip() if activity.text else ""
        
        if user_text.lower() == '/voice':
            return await self._handle_voice_command(turn_context)
        elif user_text.lower() == '/voices':
            return await self._handle_voices_command(turn_context)
        elif user_text.lower() == '/help':
            return await self._handle_help_command(turn_context)
        else:
            # Regular echo functionality
            response_text = f"Echo: {user_text}"
            return await turn_context.send_activity(response_text)

    async def _handle_audio_message(self, turn_context: TurnContext, attachment) -> None:
        """Handle incoming audio messages."""
        if not self.voice_service.is_available():
            await turn_context.send_activity(
                "Voice features are not available. Please configure Azure Speech Service."
            )
            return
        
        try:
            # In a real implementation, you would download the audio attachment
            # For now, we'll send a placeholder response
            await turn_context.send_activity(
                "I received an audio message! Voice processing is configured but would need "
                "additional implementation to download and process the audio data from the attachment."
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
        help_text += "- Type any text to get an echo response\n"
        help_text += "- Send audio messages for voice processing (if configured)\n"
        help_text += "- /voice - Enable voice session\n"
        help_text += "- /voices - List available voices\n"
        help_text += "- /help - Show this help message\n"
        
        if self.voice_service.is_available():
            help_text += "\n✅ Voice features are enabled!"
        else:
            help_text += "\n❌ Voice features are disabled. Configure Azure Speech Service to enable them."
        
        await turn_context.send_activity(help_text)