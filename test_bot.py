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
        """Test the echo functionality"""
        # Create a mock turn context
        mock_turn_context = Mock(spec=TurnContext)
        mock_turn_context.activity = Mock(spec=Activity)
        mock_turn_context.activity.text = "Hello, Bot!"
        mock_turn_context.send_activity = AsyncMock()

        # Call the method
        await self.bot.on_message_activity(mock_turn_context)

        # Verify the echo response
        mock_turn_context.send_activity.assert_called_once_with("Echo: Hello, Bot!")

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

        # Verify the welcome message
        mock_turn_context.send_activity.assert_called_once_with("Hello and welcome!")

    def test_sync_wrapper_for_echo(self):
        """Synchronous wrapper for async echo test"""
        asyncio.run(self.test_on_message_activity())

    def test_sync_wrapper_for_welcome(self):
        """Synchronous wrapper for async welcome test"""
        asyncio.run(self.test_on_members_added_activity())


if __name__ == "__main__":
    unittest.main()