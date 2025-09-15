#!/usr/bin/env python3
"""
Simple startup script for the Echo Bot
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from app import init_func
        from aiohttp import web
        from config import DefaultConfig
        
        print("Starting Echo Bot...")
        print(f"Bot will be available at: http://localhost:{DefaultConfig.PORT}/api/messages")
        print("Press CTRL+C to stop the bot")
        
        app = init_func(None)
        web.run_app(app, host="localhost", port=DefaultConfig.PORT)
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)