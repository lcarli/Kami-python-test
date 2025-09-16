#!/usr/bin/env python3
"""
Kami Bot - Hybrid Mode Only
Unified interface combining text chat and voice live conversation.
"""

import asyncio
import os
import signal
import sys
import time
import webbrowser
from pathlib import Path

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle interrupt signals for graceful shutdown"""
    global shutdown_requested
    print("Interrupt signal received...")
    shutdown_requested = True

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

async def start_hybrid():
    """Start the hybrid bot server"""
    try:
        print("Starting Kami Hybrid Bot...")
        
        # Import and start hybrid bot
        from hybrid_bot import HybridBot
        
        hybrid_bot = HybridBot()
        runner = await hybrid_bot.start_server()
        
        # Wait for server to be ready
        print("Waiting for Hybrid Bot...")
        await asyncio.sleep(3)
        
        print("Hybrid Bot is ready!")
        print()
        print("SERVICE STATUS:")
        print("----------------------------------------")
        print("Kami Hybrid Bot: RUNNING")
        print("   • Text Chat: http://localhost:3978")
        print("   • Voice Live: http://localhost:3978/hybrid")
        print()
        print("FEATURES:")
        print("• Text chat with AI agent")
        print("• Voice Live conversation with Azure")
        print("• Seamless switching between text and voice")
        print("• AI-powered responses")
        print()
        print("⌨CONTROLS:")
        print("• Ctrl+C: Stop server")
        print()
        
        # Open browser
        try:
            webbrowser.open("http://localhost:3978/hybrid")
            print("Browser opened to http://localhost:3978/hybrid")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please open: http://localhost:3978/hybrid")
        
        print("Kami Hybrid Bot started successfully!")
        print("Ready for text and voice conversations!")
        
        # Keep the server running
        try:
            while not shutdown_requested:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            await runner.cleanup()
        
    except Exception as e:
        print(f"Error starting Hybrid Bot: {e}")
        return False
    
    return True

async def main():
    """Main entry point"""
    try:
        # Setup signal handlers
        setup_signal_handlers()
        
        # Print header
        print("KAMI HYBRID BOT")
        print("=" * 50)
        print("AI-Powered Text & Voice Conversation")
        print("Azure Voice Live Integration")
        print("Seamless Hybrid Interface")
        print("=" * 50)
        print()
        
        # Start hybrid mode
        success = await start_hybrid()
        
        if not success:
            print("Failed to start Kami Hybrid Bot")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    finally:
        print("👋 Kami Hybrid Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())