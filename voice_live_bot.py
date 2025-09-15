"""
Voice Live Bot Integration
Connects Azure Voice Live API with existing bot logic for real-time voice conversations
"""

import os
import logging
import asyncio
from datetime import datetime
from aiohttp import web, WSMsgType
from aiohttp.web import Application, Request, Response, WebSocketResponse
from aiohttp_cors import setup as cors_setup, CorsConfig

from bot import EchoBot
from config import DefaultConfig
from voice_live_service import VoiceLiveService

logger = logging.getLogger(__name__)

class VoiceLiveBot:
    """Voice Live Bot with real-time conversation capabilities"""
    
    def __init__(self):
        # Initialize bot components
        self.config = DefaultConfig()
        self.bot = EchoBot()
        self.voice_live_service = None
        
        # Web app for serving Voice Live web client
        self.app = Application()
        self.setup_routes()
        self.setup_cors()
        
        # Session state
        self.conversation_history = []
        self.current_session = None

    def setup_routes(self):
        """Setup web application routes"""
        self.app.router.add_get("/", self.index_handler)
        self.app.router.add_get("/voice-live", self.voice_live_page)
        self.app.router.add_post("/api/voice-live/start", self.start_voice_live_session)
        self.app.router.add_post("/api/voice-live/stop", self.stop_voice_live_session)
        self.app.router.add_get("/api/voice-live/status", self.get_voice_live_status)
        self.app.router.add_get("/api/voice-live/ws", self.websocket_handler)

    def setup_cors(self):
        """Setup CORS for web application"""
        # Simple CORS setup - allow all origins for development
        cors = cors_setup(self.app)
        
        # Add CORS to all existing routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def index_handler(self, request: Request) -> Response:
        """Serve index page"""
        return Response(text="""
<!DOCTYPE html>
<html>
<head>
    <title>Kami Voice Live Bot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .button { background: #3498db; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; font-size: 16px; text-decoration: none; display: inline-block; }
        .button:hover { background: #2980b9; }
        .description { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .feature { margin: 15px 0; padding: 10px; border-left: 4px solid #3498db; background: #f8f9fa; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.ready { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Kami Voice Live Bot</h1>
        
        <div class="description">
            <h3>Real-time Voice Agent with Azure AI Foundry</h3>
            <p>Experience natural conversations with Kami using advanced Azure Voice Live technology. 
            This integration provides real-time voice interaction with your AI assistant.</p>
        </div>

        <div class="feature">
            <strong>🎤 Real-time Voice Recognition:</strong> Speak naturally and get instant responses
        </div>
        
        <div class="feature">
            <strong>🔊 Natural Voice Synthesis:</strong> High-quality AI voice responses
        </div>
        
        <div class="feature">
            <strong>🧠 AI-Powered Conversations:</strong> GPT-4o powered responses through Azure AI Foundry
        </div>
        
        <div class="feature">
            <strong>⚡ Low Latency:</strong> Optimized for real-time conversation flow
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <a href="/voice-live" class="button">🎙️ Start Voice Live Session</a>
        </div>

        <div class="status ready">
            <strong>Status:</strong> Voice Live Bot is ready for real-time conversations
        </div>
    </div>
</body>
</html>
        """, content_type="text/html")

    async def voice_live_page(self, request: Request) -> Response:
        """Serve Voice Live interface page"""
        return Response(text="""
<!DOCTYPE html>
<html>
<head>
    <title>Kami Voice Live - Real-time Conversation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: rgba(255, 255, 255, 0.1); 
            padding: 30px; 
            border-radius: 20px; 
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        h1 { 
            text-align: center; 
            margin-bottom: 30px; 
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .controls { 
            text-align: center; 
            margin: 30px 0; 
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .button { 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            padding: 15px 30px; 
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .button:hover { 
            background: rgba(255, 255, 255, 0.3); 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .button:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
            transform: none;
        }
        .status { 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0; 
            text-align: center;
            backdrop-filter: blur(5px);
        }
        .status.connecting { background: rgba(255, 193, 7, 0.2); border: 1px solid rgba(255, 193, 7, 0.5); }
        .status.connected { background: rgba(40, 167, 69, 0.2); border: 1px solid rgba(40, 167, 69, 0.5); }
        .status.error { background: rgba(220, 53, 69, 0.2); border: 1px solid rgba(220, 53, 69, 0.5); }
        .status.disconnected { background: rgba(108, 117, 125, 0.2); border: 1px solid rgba(108, 117, 125, 0.5); }
        
        .conversation { 
            max-height: 400px; 
            overflow-y: auto; 
            border: 1px solid rgba(255, 255, 255, 0.2); 
            border-radius: 15px; 
            padding: 20px; 
            margin: 20px 0;
            background: rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(5px);
        }
        .message { 
            margin: 10px 0; 
            padding: 10px 15px; 
            border-radius: 10px; 
            max-width: 80%;
        }
        .user-message { 
            background: rgba(0, 123, 255, 0.3); 
            margin-left: auto; 
            text-align: right;
            border: 1px solid rgba(0, 123, 255, 0.5);
        }
        .assistant-message { 
            background: rgba(40, 167, 69, 0.3); 
            margin-right: auto;
            border: 1px solid rgba(40, 167, 69, 0.5);
        }
        .timestamp { 
            font-size: 0.8em; 
            opacity: 0.7; 
            margin-top: 5px;
        }
        
        .audio-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin: 0 10px;
            background: rgba(255, 255, 255, 0.3);
        }
        .audio-indicator.recording {
            background: #dc3545;
            animation: pulse 1s infinite;
        }
        .audio-indicator.playing {
            background: #28a745;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .info-panel {
            background: rgba(0, 0, 0, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .feature-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Kami Voice Live</h1>
        
        <div class="info-panel">
            <h3>🚀 Real-time Voice AI Conversation</h3>
            <p>Experience natural conversations with your AI assistant using Azure Voice Live technology. 
            Start a session to begin talking with Kami in real-time.</p>
            
            <div class="feature-list">
                <div class="feature-item">
                    <strong>🎤 Voice Recognition</strong><br>
                    Advanced speech-to-text with noise suppression
                </div>
                <div class="feature-item">
                    <strong>🧠 AI Processing</strong><br>
                    GPT-4o powered responses via Azure AI Foundry
                </div>
                <div class="feature-item">
                    <strong>🔊 Voice Synthesis</strong><br>
                    Natural-sounding voice responses
                </div>
                <div class="feature-item">
                    <strong>⚡ Real-time</strong><br>
                    Low-latency conversation flow
                </div>
            </div>
        </div>

        <div class="controls">
            <button id="startBtn" class="button">🎙️ Start Voice Live Session</button>
            <button id="stopBtn" class="button" disabled>🛑 Stop Session</button>
            <span class="audio-indicator" id="audioIndicator"></span>
        </div>

        <div id="status" class="status disconnected">
            📡 Ready to start Voice Live session
        </div>

        <div class="conversation" id="conversation">
            <div class="message assistant-message">
                <div>👋 Hello! I'm Kami, your AI assistant. Click "Start Voice Live Session" to begin our real-time conversation!</div>
                <div class="timestamp">Ready to talk</div>
            </div>
        </div>
    </div>

    <script>
        let isSessionActive = false;
        let websocket = null;
        
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        const conversation = document.getElementById('conversation');
        const audioIndicator = document.getElementById('audioIndicator');

        startBtn.addEventListener('click', startVoiceLiveSession);
        stopBtn.addEventListener('click', stopVoiceLiveSession);

        async function startVoiceLiveSession() {
            try {
                updateStatus('connecting', '🔄 Starting Voice Live session...');
                
                const response = await fetch('/api/voice-live/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    isSessionActive = true;
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    
                    updateStatus('connected', '🎙️ Voice Live session active - Start speaking!');
                    addMessage('assistant', 'Voice Live session started! You can now speak naturally and I will respond with voice.');
                    
                    // Connect WebSocket for real-time updates
                    connectWebSocket();
                } else {
                    throw new Error(result.error || 'Failed to start session');
                }
            } catch (error) {
                updateStatus('error', `❌ Error: ${error.message}`);
                console.error('Failed to start Voice Live session:', error);
            }
        }

        async function stopVoiceLiveSession() {
            try {
                updateStatus('connecting', '🔄 Stopping Voice Live session...');
                
                const response = await fetch('/api/voice-live/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                isSessionActive = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                audioIndicator.className = 'audio-indicator';
                
                if (websocket) {
                    websocket.close();
                    websocket = null;
                }
                
                updateStatus('disconnected', '📡 Voice Live session stopped');
                addMessage('assistant', 'Voice Live session ended. Click "Start Voice Live Session" to begin again.');
                
            } catch (error) {
                updateStatus('error', `❌ Error stopping session: ${error.message}`);
                console.error('Failed to stop Voice Live session:', error);
            }
        }

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/voice-live/ws`;
            
            websocket = new WebSocket(wsUrl);
            
            websocket.onopen = function(event) {
                console.log('WebSocket connected');
            };
            
            websocket.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    handleVoiceLiveEvent(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            websocket.onclose = function(event) {
                console.log('WebSocket disconnected');
                if (isSessionActive) {
                    // Try to reconnect if session is still active
                    setTimeout(connectWebSocket, 2000);
                }
            };
            
            websocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        function handleVoiceLiveEvent(data) {
            const { event_type, data: eventData } = data;
            
            switch (event_type) {
                case 'user_transcript':
                    addMessage('user', eventData.text);
                    audioIndicator.className = 'audio-indicator';
                    break;
                    
                case 'agent_audio_transcript':
                    addMessage('assistant', eventData.text);
                    audioIndicator.className = 'audio-indicator playing';
                    break;
                    
                case 'speech_started':
                    audioIndicator.className = 'audio-indicator recording';
                    break;
                    
                case 'session_created':
                    updateStatus('connected', `🎙️ Voice Live session active (ID: ${eventData.session_id})`);
                    break;
                    
                case 'error':
                    updateStatus('error', `❌ Voice Live Error: ${eventData.message}`);
                    break;
                    
                default:
                    console.log('Unknown event type:', event_type, eventData);
            }
        }

        function updateStatus(type, message) {
            status.className = `status ${type}`;
            status.textContent = message;
        }

        function addMessage(sender, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const timestamp = new Date().toLocaleTimeString();
            messageDiv.innerHTML = `
                <div>${text}</div>
                <div class="timestamp">${timestamp}</div>
            `;
            
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }

        // Check session status on page load
        window.addEventListener('load', async function() {
            try {
                const response = await fetch('/api/voice-live/status');
                const result = await response.json();
                
                if (result.active) {
                    updateStatus('connected', '🎙️ Voice Live session already active');
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    isSessionActive = true;
                    connectWebSocket();
                }
            } catch (error) {
                console.error('Error checking session status:', error);
            }
        });
    </script>
</body>
</html>
        """, content_type="text/html")

    async def start_voice_live_session(self, request: Request) -> Response:
        """Start Voice Live session"""
        try:
            if self.voice_live_service and self.voice_live_service.running:
                return web.json_response({"success": False, "error": "Session already active"})
            
            # Create Voice Live service with callback
            self.voice_live_service = VoiceLiveService(callback_handler=self.voice_live_callback)
            
            # Start session
            success = self.voice_live_service.start_session()
            
            if success:
                self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
                return web.json_response({"success": True, "session_id": self.current_session})
            else:
                return web.json_response({"success": False, "error": "Failed to start Voice Live session"})
                
        except Exception as e:
            logger.error(f"Error starting Voice Live session: {e}")
            return web.json_response({"success": False, "error": str(e)})

    async def stop_voice_live_session(self, request: Request) -> Response:
        """Stop Voice Live session"""
        try:
            if self.voice_live_service:
                self.voice_live_service.stop_session()
                self.voice_live_service = None
            
            self.current_session = None
            return web.json_response({"success": True})
            
        except Exception as e:
            logger.error(f"Error stopping Voice Live session: {e}")
            return web.json_response({"success": False, "error": str(e)})

    async def get_voice_live_status(self, request: Request) -> Response:
        """Get Voice Live session status"""
        active = self.voice_live_service and self.voice_live_service.running
        return web.json_response({
            "active": active,
            "session_id": self.current_session if active else None
        })

    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """WebSocket handler for real-time Voice Live events"""
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        # Store WebSocket for sending events
        if not hasattr(self, 'websockets'):
            self.websockets = set()
        self.websockets.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = msg.json()
                        logger.info(f"WebSocket message: {data}")
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            if hasattr(self, 'websockets'):
                self.websockets.discard(ws)
        
        return ws

    def voice_live_callback(self, event_type: str, data: dict):
        """Callback handler for Voice Live events"""
        logger.info(f"Voice Live event: {event_type} - {data}")
        
        # Store conversation history
        if event_type in ["user_transcript", "agent_audio_transcript"]:
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": event_type,
                "text": data.get("text", "")
            })
        
        # Send event to connected WebSocket clients
        if hasattr(self, 'websockets'):
            message = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected WebSocket clients
            disconnected = set()
            for ws in self.websockets:
                try:
                    # Use asyncio to send message
                    asyncio.create_task(ws.send_str(str(message).replace("'", '"')))
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    disconnected.add(ws)
            
            # Clean up disconnected clients
            self.websockets -= disconnected

    def create_app(self) -> Application:
        """Create and return the web application"""
        return self.app

def create_voice_live_bot() -> Application:
    """Factory function to create Voice Live Bot application"""
    bot = VoiceLiveBot()
    return bot.create_app()

if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    )
    
    # Create bot application
    voice_live_bot = VoiceLiveBot()
    app = voice_live_bot.create_app()
    
    # Get port from config
    config = DefaultConfig()
    port = config.PORT
    
    print(f"[VOICE LIVE] Starting Kami Voice Live Bot on port {port}")
    print(f"   [WEB] Web interface: http://localhost:{port}")
    print(f"   [VOICE] Voice Live: http://localhost:{port}/voice-live")
    print("   [INFO] Press Ctrl+C to stop")
    
    try:
        from aiohttp import web
        web.run_app(app, host="localhost", port=port)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Voice Live Bot...")
        if voice_live_bot.voice_live_service:
            voice_live_bot.voice_live_service.stop_session()
        print("✅ Voice Live Bot stopped")