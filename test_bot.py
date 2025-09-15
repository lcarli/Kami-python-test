#!/usr/bin/env python3
# Simple test to verify bot functionality

import asyncio
import unittest
from unittest.mock import Mock, AsyncMock

from botbuilder.core import TurnContext
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount

from bot import EchoBot


class TestEchoBot(unittest.TestCase):
    def setUp(self):
        self.bot = EchoBot()

    def test_echo_bot_creation(self):
        """Test that EchoBot can be instantiated"""
        self.assertIsInstance(self.bot, EchoBot)

    async def test_on_message_activity(self):
        """Test the AI agent functionality"""
        # Create a mock turn context
        mock_turn_context = Mock(spec=TurnContext)
        mock_turn_context.activity = Mock(spec=Activity)
        mock_turn_context.activity.text = "Hello, Bot!"
        mock_turn_context.activity.attachments = None  # Fix for attachments attribute
        mock_turn_context.send_activity = AsyncMock()

        # Call the method
        await self.bot.on_message_activity(mock_turn_context)

        # Verify that send_activity was called (AI response instead of echo)
        mock_turn_context.send_activity.assert_called_once()
        # Get the actual call arguments
        call_args = mock_turn_context.send_activity.call_args[0][0]
        # Verify it's not the old echo format and contains AI assistant response
        self.assertNotIn("Echo:", call_args)
        self.assertIn("AI assistant bot", call_args)

    async def test_on_members_added_activity(self):
        """Test the welcome message functionality"""
        # Create mock objects
        mock_turn_context = Mock(spec=TurnContext)
        mock_turn_context.activity = Mock(spec=Activity)
        mock_turn_context.activity.recipient = Mock(spec=ChannelAccount)
        mock_turn_context.activity.recipient.id = "bot_id"
        mock_turn_context.send_activity = AsyncMock()

        # Create mock member
        mock_member = Mock(spec=ChannelAccount)
        mock_member.id = "user_id"  # Different from bot ID
        members_added = [mock_member]

        # Call the method
        await self.bot.on_members_added_activity(members_added, mock_turn_context)

        # Verify the welcome message was sent
        mock_turn_context.send_activity.assert_called_once()
        # Get the actual call arguments
        call_args = mock_turn_context.send_activity.call_args[0][0]
        # Verify it contains AI assistant welcome
        self.assertIn("AI assistant bot", call_args)
        self.assertIn("voice capabilities", call_args)

    def test_sync_wrapper_for_echo(self):
        """Synchronous wrapper for async echo test"""
        asyncio.run(self.test_on_message_activity())

    def test_sync_wrapper_for_welcome(self):
        """Synchronous wrapper for async welcome test"""
        asyncio.run(self.test_on_members_added_activity())

    async def test_ai_agent_fallback_response(self):
        """Test AI agent fallback functionality when service is not configured"""
        # Create a mock turn context for a greeting
        mock_turn_context = Mock(spec=TurnContext)
        mock_turn_context.activity = Mock(spec=Activity)
        mock_turn_context.activity.text = "Hello"
        mock_turn_context.activity.attachments = None
        mock_turn_context.send_activity = AsyncMock()

        # Call the method
        await self.bot.on_message_activity(mock_turn_context)

        # Verify appropriate fallback response for greeting
        mock_turn_context.send_activity.assert_called_once()
        call_args = mock_turn_context.send_activity.call_args[0][0]
        self.assertIn("Hello", call_args)
        self.assertIn("AI assistant bot", call_args)

    def test_sync_wrapper_for_ai_agent(self):
        """Synchronous wrapper for async AI agent test"""
        asyncio.run(self.test_ai_agent_fallback_response())


if __name__ == "__main__":
    unittest.main()