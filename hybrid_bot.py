#!/usr/bin/env python3
"""
Hybrid Bot - Unified interface combining text chat and voice live conversation.
Users can start with text and seamlessly switch to voice mode.
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from aiohttp import web, WSMsgType
from aiohttp.web import Application, Request, Response, WebSocketResponse
import aiohttp_cors

from bot import EchoBot
from config import DefaultConfig
from voice_live_service import VoiceLiveService

logger = logging.getLogger(__name__)

class HybridBot:
    """
    Hybrid bot that combines text chat and voice live conversation.
    Provides seamless switching between text and voice modes.
    """
    
    def __init__(self):
        # Initialize bot components
        self.config = DefaultConfig()
        self.bot = EchoBot()
        self.voice_live_service = None
        self.current_voice_connection = None
        
        # Web app for serving hybrid interface
        self.app = Application()
        self.setup_routes()
        self.setup_cors()
        
        # Active connections tracking
        self.websockets = set()
        self.voice_sessions = {}  # track voice sessions per connection
        
        # Initialize Voice Live service
        self._init_voice_live_service()
        
    def _init_voice_live_service(self):
        """Initialize Voice Live service if credentials are available"""
        try:
            if all([
                self.config.AZURE_VOICE_LIVE_ENDPOINT,
                self.config.AZURE_VOICE_LIVE_API_KEY,
                self.config.AI_FOUNDRY_PROJECT_NAME,
                self.config.AI_FOUNDRY_AGENT_ID
            ]):
                self.voice_live_service = VoiceLiveService(self.config)
                logger.info("Voice Live service initialized successfully")
            else:
                logger.warning("Voice Live service not available - missing configuration")
        except Exception as e:
            logger.error(f"Failed to initialize Voice Live service: {e}")
    
    def setup_cors(self):
        """Setup CORS for web application"""
        # Simple CORS setup - allow all origins for development
        cors = aiohttp_cors.setup(self.app)
        
        # Add CORS to all existing routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_routes(self):
        """Setup web routes"""
        # Main hybrid interface
        self.app.router.add_get("/", self.serve_hybrid_interface)
        self.app.router.add_get("/hybrid", self.serve_hybrid_interface)
        
        # WebSocket for real-time communication
        self.app.router.add_get("/ws", self.websocket_handler)
        
        # Text chat API
        self.app.router.add_post("/api/chat", self.handle_text_message)
        
        # Voice Live API endpoints
        self.app.router.add_post("/api/voice/start", self.start_voice_session)
        self.app.router.add_post("/api/voice/stop", self.stop_voice_session)
        self.app.router.add_get("/api/voice/ws", self.voice_websocket_handler)
        
        # Static files
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.router.add_static("/static/", path=static_dir, name="static")
            logger.info(f"Serving static files from: {static_dir}")
        else:
            logger.warning("Static directory not found - creating it")
            static_dir.mkdir(exist_ok=True)

    async def serve_hybrid_interface(self, request: Request) -> Response:
        """Serve the main hybrid chat interface"""
        # Serve the static HTML file
        static_path = Path(__file__).parent / "static" / "index.html"
        
        if static_path.exists():
            with open(static_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return Response(text=html_content, content_type="text/html")
        else:
            # Fallback to inline HTML if static file doesn't exist
            return Response(text=self.get_fallback_html(), content_type="text/html")

    def get_fallback_html(self) -> str:
        """Fallback HTML if static files are not available"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kami - Hybrid Chat & Voice Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            color: #333;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Kami Assistant</h1>
        <p>Static files not found. Please ensure the static directory exists with the required files.</p>
        <p>Expected files:</p>
        <ul>
            <li>static/index.html</li>
            <li>static/styles.css</li>
            <li>static/script.js</li>
        </ul>
    </div>
</body>
</html>
        """

    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """Handle WebSocket connections for real-time communication"""
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        logger.info("New WebSocket connection established")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_websocket_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON format'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
            logger.info("WebSocket connection closed")
        
        return ws

    async def handle_websocket_message(self, ws: WebSocketResponse, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = data.get('type')
            
            if message_type == 'ping':
                await ws.send_str(json.dumps({'type': 'pong'}))
            elif message_type == 'text_message':
                # Handle text message through bot
                response = await self.process_text_message(data.get('message', ''))
                await ws.send_str(json.dumps({
                    'type': 'text_response',
                    'message': response
                }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_text_message(self, request: Request) -> Response:
        """Handle text chat messages"""
        try:
            data = await request.json()
            message = data.get('message', '')
            
            if not message:
                return web.json_response({
                    'success': False,
                    'error': 'Message is required'
                }, status=400)
            
            # Process message through bot
            response = await self.process_text_message(message)
            
            return web.json_response({
                'success': True,
                'response': response
            })
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def process_text_message(self, message: str) -> str:
        """Process text message through the bot"""
        try:
            # Use the bot's AI service to generate response
            if self.bot.ai_agent_service and self.bot.ai_agent_service.is_available():
                # Add to conversation history
                self.bot.conversation_history.add_user_message(message)
                
                # Get AI response
                ai_response = await self.bot.ai_agent_service.get_response(
                    message, 
                    self.bot.conversation_history.get_history()
                )
                
                if ai_response:
                    self.bot.conversation_history.add_assistant_message(ai_response)
                    return ai_response
            
            # Fallback response
            return f"I received your message: '{message}'. How can I help you further?"
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return "I'm sorry, I encountered an error processing your message. Please try again."

    async def start_voice_session(self, request: Request) -> Response:
        """Start a voice live session"""
        try:
            if not self.voice_live_service:
                return web.json_response({
                    'success': False,
                    'error': 'Voice Live service not available'
                }, status=503)
            
            # Initialize voice session
            session_id = f"session_{int(time.time())}"
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'message': 'Voice session started'
            })
            
        except Exception as e:
            logger.error(f"Error starting voice session: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def stop_voice_session(self, request: Request) -> Response:
        """Stop a voice live session"""
        try:
            data = await request.json()
            session_id = data.get('session_id')
            
            if session_id in self.voice_sessions:
                del self.voice_sessions[session_id]
            
            return web.json_response({
                'success': True,
                'message': 'Voice session stopped'
            })
            
        except Exception as e:
            logger.error(f"Error stopping voice session: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def voice_websocket_handler(self, request: Request) -> WebSocketResponse:
        """Handle WebSocket connections for voice live - Integrate with real Voice Live service"""
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        logger.info("New Voice WebSocket connection established")
        
        try:
            if self.voice_live_service:
                # Initialize Voice Live connection
                await ws.send_str(json.dumps({
                    'type': 'status',
                    'message': 'Voice Live connection established'
                }))
                
                # Start Voice Live session in background
                session_task = asyncio.create_task(self._handle_voice_live_session(ws))
                
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            await self.handle_voice_websocket_message(ws, data)
                        except json.JSONDecodeError:
                            await ws.send_str(json.dumps({
                                'type': 'error',
                                'message': 'Invalid JSON format'
                            }))
                    elif msg.type == WSMsgType.BINARY:
                        # Voice Live handles audio directly from microphone - ignore browser audio
                        logger.debug(f"Ignoring browser audio data: {len(msg.data)} bytes")
                    elif msg.type == WSMsgType.ERROR:
                        logger.error(f'Voice WebSocket error: {ws.exception()}')
                
                # Clean up session task
                session_task.cancel()
                try:
                    await session_task
                except asyncio.CancelledError:
                    pass
            else:
                await ws.send_str(json.dumps({
                    'type': 'error',
                    'message': 'Voice Live service not available'
                }))
        except Exception as e:
            logger.error(f"Voice WebSocket error: {e}")
        finally:
            logger.info("Voice WebSocket connection closed")
        
        return ws
    
    async def _handle_voice_live_session(self, ws: WebSocketResponse):
        """Handle Voice Live session with Azure API"""
        try:
            if not self.voice_live_service:
                await ws.send_str(json.dumps({
                    'type': 'error',
                    'message': 'Voice Live service not available'
                }))
                return
            
            # Set up callback handler to bridge Voice Live events to WebSocket
            # Store the current event loop reference
            main_loop = asyncio.get_running_loop()
            
            def voice_live_callback(event_type, data):
                # This runs in a separate thread, so we need to handle async properly
                try:
                    # Use the stored main loop reference
                    if main_loop and not main_loop.is_closed():
                        # Schedule the coroutine to run in the main loop
                        asyncio.run_coroutine_threadsafe(
                            self._send_voice_event_to_ws(ws, event_type, data), 
                            main_loop
                        )
                    else:
                        logger.warning("Main event loop not available, cannot send voice event")
                except Exception as e:
                    logger.error(f"Error in voice callback: {e}")
            
            # Update callback handler
            self.voice_live_service.callback_handler = voice_live_callback
            
            # Initialize Voice Live connection
            await ws.send_str(json.dumps({
                'type': 'voice_live_connected',
                'message': 'Connecting to Azure Voice Live API...'
            }))
            
            # Start Voice Live session in a thread (it's blocking)
            async def start_voice_session_async():
                try:
                    # Run the blocking Voice Live session in a thread executor
                    loop = asyncio.get_running_loop()
                    success = await loop.run_in_executor(
                        None, self.voice_live_service.start_session
                    )
                    if success:
                        logger.info("Voice Live session started successfully")
                    else:
                        logger.error("Failed to start Voice Live session")
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Failed to start Voice Live session'
                        }))
                except Exception as e:
                    logger.error(f"Exception starting Voice Live session: {e}")
                    await ws.send_str(json.dumps({
                        'type': 'error',
                        'message': f'Voice Live error: {str(e)}'
                    }))
            
            # Start Voice Live session
            voice_task = asyncio.create_task(start_voice_session_async())
            
            # Give it a moment to start
            await asyncio.sleep(2)
            
            await ws.send_str(json.dumps({
                'type': 'voice_live_started',
                'message': 'Voice Live conversation started. Speak into your microphone.'
            }))
            
            # Keep session alive while Voice Live is running
            try:
                while self.voice_live_service and self.voice_live_service.running:
                    await asyncio.sleep(0.5)
                    
            except asyncio.CancelledError:
                if self.voice_live_service:
                    # Stop in executor to avoid blocking
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, self.voice_live_service.stop_session)
                raise
                
        except asyncio.CancelledError:
            logger.info("Voice Live session cancelled")
        except Exception as e:
            logger.error(f"Error in Voice Live session: {e}")
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': f'Voice Live session error: {str(e)}'
            }))
    
    async def _send_voice_event_to_ws(self, ws: WebSocketResponse, event_type: str, data: dict):
        """Send Voice Live events to WebSocket client"""
        try:
            if event_type == "user_transcript":
                await ws.send_str(json.dumps({
                    'type': 'transcript',
                    'text': data.get('text', '')
                }))
                
            elif event_type == "agent_text":
                await ws.send_str(json.dumps({
                    'type': 'response_text',
                    'text': data.get('text', '')
                }))
                
            elif event_type == "agent_audio_transcript":
                await ws.send_str(json.dumps({
                    'type': 'audio_transcript',
                    'text': data.get('text', '')
                }))
                
            elif event_type == "session_created":
                await ws.send_str(json.dumps({
                    'type': 'session_created',
                    'session_id': data.get('session_id', '')
                }))
                
            elif event_type == "speech_started":
                await ws.send_str(json.dumps({
                    'type': 'speech_started',
                    'message': 'User started speaking'
                }))
                
            elif event_type == "error":
                await ws.send_str(json.dumps({
                    'type': 'error',
                    'message': data.get('message', 'Unknown error')
                }))
                
        except Exception as e:
            logger.error(f"Error sending voice event to WebSocket: {e}")

    async def handle_voice_websocket_message(self, ws: WebSocketResponse, data: Dict[str, Any]):
        """Handle voice WebSocket messages"""
        try:
            message_type = data.get('type')
            
            if message_type == 'start_conversation':
                # Voice Live session is already started by _handle_voice_live_session
                # Just acknowledge the request
                await ws.send_str(json.dumps({
                    'type': 'status',
                    'message': 'Voice Live session already active'
                }))
                    
            elif message_type == 'stop_conversation':
                # Stop the Voice Live service
                if self.voice_live_service:
                    self.voice_live_service.stop_session()
                    
                await ws.send_str(json.dumps({
                    'type': 'conversation_ended',
                    'message': 'Voice Live conversation stopped'
                }))
                
            elif message_type == 'voice_message':
                # This should not be used with real Voice Live - audio goes directly from microphone
                logger.debug("Received voice_message - this should not happen with Voice Live")
                    
        except Exception as e:
            logger.error(f"Error handling voice WebSocket message: {e}")
            await ws.send_str(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    def create_app(self) -> Application:
        """Create and configure the web application"""
        return self.app

    async def start_server(self, host: str = "localhost", port: int = 3978):
        """Start the hybrid bot server"""
        try:
            logger.info(f"Starting Hybrid Bot server on {host}:{port}")
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            logger.info(f"Hybrid Bot server started successfully on http://{host}:{port}")
            return runner
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise

async def main():
    """Main entry point for hybrid bot"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create hybrid bot instance
    hybrid_bot = HybridBot()
    
    # Get port from config
    config = DefaultConfig()
    port = config.PORT
    
    print(f"[HYBRID] Starting Kami Hybrid Bot on port {port}")
    print(f"   [WEB] Interface: http://localhost:{port}")
    print(f"   [CHAT] Text & Voice: http://localhost:{port}/hybrid")
    print("   [INFO] Press Ctrl+C to stop")
    
    try:
        # Start the server
        runner = await hybrid_bot.start_server(port=port)
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"[ERROR] Failed to start server: {e}")

if __name__ == "__main__":
    asyncio.run(main())