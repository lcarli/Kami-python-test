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
        
        # Static files (optional - create directory if needed)
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.router.add_static("/static/", path=static_dir, name="static")

    async def serve_hybrid_interface(self, request: Request) -> Response:
        """Serve the main hybrid chat interface"""
        html_content = self.get_hybrid_interface_html()
        return Response(text=html_content, content_type="text/html")

    def get_hybrid_interface_html(self) -> str:
        """Generate the hybrid interface HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kami - Hybrid Chat & Voice Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-title {
            font-size: 24px;
            font-weight: bold;
        }
        
        .mode-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toggle-button {
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .toggle-button:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .toggle-button.active {
            background: white;
            color: #667eea;
            border-color: white;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 5px;
        }
        
        .status-text { color: #ccc; }
        .status-ready { background: #4CAF50; }
        .status-listening { background: #FF9800; animation: pulse 1s infinite; }
        .status-speaking { background: #2196F3; animation: pulse 1s infinite; }
        .status-error { background: #F44336; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 20px;
            word-wrap: break-word;
        }
        
        .message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message.bot .message-bubble {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 5px;
        }
        
        .message-time {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button, .voice-button {
            width: 50px;
            height: 50px;
            border: none;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: all 0.3s ease;
        }
        
        .send-button:hover, .voice-button:hover {
            transform: scale(1.1);
        }
        
        .voice-button.listening {
            background: linear-gradient(135deg, #FF9800 0%, #FF5722 100%);
            animation: pulse 1s infinite;
        }
        
        .voice-button.speaking {
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
            animation: pulse 1s infinite;
        }
        
        .text-mode-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .voice-mode-controls {
            display: none;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }
        
        .voice-controls-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .voice-status {
            font-size: 14px;
            color: #666;
            text-align: center;
        }
        
        .mode-voice .text-mode-controls {
            display: none;
        }
        
        .mode-voice .voice-mode-controls {
            display: flex;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 20px;
            color: #666;
            font-style: italic;
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 5px;
            margin: 10px;
            border-left: 4px solid #c62828;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="chat-title">🤖 Kami Assistant</div>
            <div class="mode-toggle">
                <button class="toggle-button active" id="text-mode-btn">💬 Text</button>
                <button class="toggle-button" id="voice-mode-btn">🎙️ Voice</button>
                <div class="status-indicator status-ready" id="status-indicator"></div>
            </div>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="message bot">
                <div class="message-bubble">
                    Hello! I'm Kami, your AI assistant. You can chat with me using text or switch to voice mode for voice conversations. How can I help you today?
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typing-indicator">
            Kami is typing...
        </div>
        
        <div class="chat-input-container mode-text" id="input-container">
            <div class="text-mode-controls">
                <input type="text" class="chat-input" id="chat-input" placeholder="Type your message..." />
                <button class="send-button" id="send-button">📤</button>
                <button class="voice-button" id="voice-button">🎙️</button>
            </div>
            
            <div class="voice-mode-controls">
                <div class="voice-controls-row">
                    <button class="voice-button" id="start-voice-button">🎙️</button>
                    <button class="voice-button" id="stop-voice-button" style="background: #f44336;">⏹️</button>
                </div>
                <div class="voice-status" id="voice-status">Click the microphone to start voice conversation</div>
            </div>
        </div>
    </div>

    <script>
        class HybridChatBot {
            constructor() {
                this.currentMode = 'text';
                this.ws = null;
                this.voiceWs = null;
                this.isVoiceActive = false;
                this.isConnected = false;
                
                this.initializeElements();
                this.setupEventListeners();
                this.connectWebSocket();
            }
            
            initializeElements() {
                this.elements = {
                    chatMessages: document.getElementById('chat-messages'),
                    chatInput: document.getElementById('chat-input'),
                    sendButton: document.getElementById('send-button'),
                    voiceButton: document.getElementById('voice-button'),
                    startVoiceButton: document.getElementById('start-voice-button'),
                    stopVoiceButton: document.getElementById('stop-voice-button'),
                    textModeBtn: document.getElementById('text-mode-btn'),
                    voiceModeBtn: document.getElementById('voice-mode-btn'),
                    inputContainer: document.getElementById('input-container'),
                    statusIndicator: document.getElementById('status-indicator'),
                    voiceStatus: document.getElementById('voice-status'),
                    typingIndicator: document.getElementById('typing-indicator')
                };
            }
            
            setupEventListeners() {
                // Mode switching
                this.elements.textModeBtn.addEventListener('click', () => this.switchMode('text'));
                this.elements.voiceModeBtn.addEventListener('click', () => this.switchMode('voice'));
                
                // Text mode
                this.elements.sendButton.addEventListener('click', () => this.sendTextMessage());
                this.elements.chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.sendTextMessage();
                });
                
                // Voice mode
                this.elements.voiceButton.addEventListener('click', () => this.toggleVoiceMode());
                this.elements.startVoiceButton.addEventListener('click', () => this.startVoiceConversation());
                this.elements.stopVoiceButton.addEventListener('click', () => this.stopVoiceConversation());
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.updateStatus('ready');
                    console.log('WebSocket connected');
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;
                    this.updateStatus('error');
                    console.log('WebSocket disconnected');
                    // Attempt to reconnect after 3 seconds
                    setTimeout(() => this.connectWebSocket(), 3000);
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateStatus('error');
                };
            }
            
            handleWebSocketMessage(data) {
                switch (data.type) {
                    case 'text_response':
                        this.addMessage('bot', data.message);
                        this.hideTypingIndicator();
                        break;
                    case 'voice_status':
                        this.updateVoiceStatus(data.status);
                        break;
                    case 'error':
                        this.showError(data.message);
                        break;
                }
            }
            
            switchMode(mode) {
                this.currentMode = mode;
                
                // Update UI
                this.elements.textModeBtn.classList.toggle('active', mode === 'text');
                this.elements.voiceModeBtn.classList.toggle('active', mode === 'voice');
                this.elements.inputContainer.className = `chat-input-container mode-${mode}`;
                
                // Stop voice if switching to text
                if (mode === 'text' && this.isVoiceActive) {
                    this.stopVoiceConversation();
                }
                
                console.log(`Switched to ${mode} mode`);
            }
            
            async sendTextMessage() {
                const message = this.elements.chatInput.value.trim();
                if (!message || !this.isConnected) return;
                
                // Add user message to chat
                this.addMessage('user', message);
                this.elements.chatInput.value = '';
                this.showTypingIndicator();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        this.addMessage('bot', data.response);
                    } else {
                        this.showError(data.error || 'Failed to send message');
                    }
                } catch (error) {
                    this.showError('Network error: ' + error.message);
                } finally {
                    this.hideTypingIndicator();
                }
            }
            
            toggleVoiceMode() {
                if (this.currentMode === 'text') {
                    this.switchMode('voice');
                }
            }
            
            async startVoiceConversation() {
                if (this.isVoiceActive) return;
                
                try {
                    this.updateStatus('listening');
                    this.isVoiceActive = true;
                    this.updateVoiceStatus('Starting Voice Live conversation...');
                    
                    // Request microphone permission
                    this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            sampleRate: 24000,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        }
                    });
                    
                    // Connect to voice WebSocket
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const voiceWsUrl = `${protocol}//${window.location.host}/api/voice/ws`;
                    
                    this.voiceWs = new WebSocket(voiceWsUrl);
                    
                    this.voiceWs.onopen = () => {
                        console.log('Voice WebSocket connected');
                        
                        // Send start conversation message
                        this.voiceWs.send(JSON.stringify({
                            'type': 'start_conversation'
                        }));
                    };
                    
                    this.voiceWs.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        this.handleVoiceMessage(data);
                    };
                    
                    this.voiceWs.onclose = () => {
                        this.updateVoiceStatus('Voice Live conversation ended');
                        console.log('Voice WebSocket disconnected');
                    };
                    
                    this.voiceWs.onerror = (error) => {
                        console.error('Voice WebSocket error:', error);
                        this.showError('Voice Live connection error');
                    };
                    
                    // Setup audio streaming to Voice Live
                    this.setupAudioStreaming();
                    
                    console.log('Voice Live conversation started');
                    
                } catch (error) {
                    this.showError('Failed to start Voice Live conversation: ' + error.message);
                    this.stopVoiceConversation();
                }
            }
            
            setupAudioStreaming() {
                try {
                    // Create audio context for processing
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                        sampleRate: 24000
                    });
                    
                    // Create source from microphone stream
                    this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
                    
                    // Create script processor for audio data
                    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
                    
                    this.processor.onaudioprocess = (event) => {
                        if (this.voiceWs && this.voiceWs.readyState === WebSocket.OPEN) {
                            const inputData = event.inputBuffer.getChannelData(0);
                            
                            // Convert to 16-bit PCM and send to Voice Live
                            const pcmData = this.convertToPCM16(inputData);
                            this.voiceWs.send(pcmData);
                        }
                    };
                    
                    // Connect audio nodes
                    this.source.connect(this.processor);
                    this.processor.connect(this.audioContext.destination);
                    
                    this.updateVoiceStatus('Voice Live active - speak now!');
                    
                } catch (error) {
                    console.error('Error setting up audio streaming:', error);
                    this.showError('Failed to setup audio streaming: ' + error.message);
                }
            }
            
            convertToPCM16(float32Array) {
                // Convert Float32Array to 16-bit PCM
                const buffer = new ArrayBuffer(float32Array.length * 2);
                const view = new DataView(buffer);
                let offset = 0;
                
                for (let i = 0; i < float32Array.length; i++, offset += 2) {
                    const s = Math.max(-1, Math.min(1, float32Array[i]));
                    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                }
                
                return buffer;
            }
            
            stopVoiceConversation() {
                if (!this.isVoiceActive) return;
                
                this.isVoiceActive = false;
                this.updateStatus('ready');
                this.updateVoiceStatus('Click the microphone to start voice conversation');
                
                // Clean up audio context and processor
                if (this.processor) {
                    this.processor.disconnect();
                    this.processor = null;
                }
                
                if (this.source) {
                    this.source.disconnect();
                    this.source = null;
                }
                
                if (this.audioContext && this.audioContext.state !== 'closed') {
                    this.audioContext.close();
                    this.audioContext = null;
                }
                
                // Stop media stream
                if (this.mediaStream) {
                    this.mediaStream.getTracks().forEach(track => track.stop());
                    this.mediaStream = null;
                }
                
                // Close voice WebSocket
                if (this.voiceWs) {
                    this.voiceWs.send(JSON.stringify({
                        'type': 'stop_conversation'
                    }));
                    this.voiceWs.close();
                    this.voiceWs = null;
                }
                
                console.log('Voice Live conversation stopped');
            }
            
            handleVoiceMessage(data) {
                try {
                    console.log('Voice message received:', data);
                    
                    switch (data.type) {
                        case 'voice_live_started':
                            this.updateVoiceStatus('Voice Live conversation started');
                            break;
                            
                        case 'voice_live_connected':
                            this.updateVoiceStatus('Connected to Azure Voice Live API');
                            break;
                            
                        case 'audio_response':
                            // Handle audio response from Voice Live
                            if (data.audio_data) {
                                this.playAudioResponse(data.audio_data);
                            }
                            break;
                            
                        case 'transcript':
                            // Handle transcript from Voice Live
                            if (data.text) {
                                this.addMessage('user', data.text);
                                this.updateVoiceStatus('Processing your message...');
                            }
                            break;
                            
                        case 'response_text':
                            // Handle text response from Voice Live
                            if (data.text) {
                                this.addMessage('bot', data.text);
                            }
                            break;
                            
                        case 'conversation_ended':
                            this.updateVoiceStatus('Voice Live conversation ended');
                            this.stopVoiceConversation();
                            break;
                            
                        case 'error':
                            this.showError('Voice Live error: ' + (data.message || 'Unknown error'));
                            break;
                            
                        default:
                            console.log('Unknown voice message type:', data.type);
                            break;
                    }
                    
                } catch (error) {
                    console.error('Error handling voice message:', error);
                    this.showError('Error handling voice message: ' + error.message);
                }
            }
            
            playAudioResponse(audioData) {
                try {
                    // Convert base64 audio data to playable format
                    const audioBytes = atob(audioData);
                    const arrayBuffer = new ArrayBuffer(audioBytes.length);
                    const uint8Array = new Uint8Array(arrayBuffer);
                    
                    for (let i = 0; i < audioBytes.length; i++) {
                        uint8Array[i] = audioBytes.charCodeAt(i);
                    }
                    
                    // Create audio context if not exists
                    if (!this.audioContext) {
                        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    }
                    
                    // Decode and play audio
                    this.audioContext.decodeAudioData(arrayBuffer)
                        .then(audioBuffer => {
                            const source = this.audioContext.createBufferSource();
                            source.buffer = audioBuffer;
                            source.connect(this.audioContext.destination);
                            
                            source.onended = () => {
                                this.updateStatus('listening');
                                this.updateVoiceStatus('Voice Live active - speak now!');
                            };
                            
                            this.updateStatus('speaking');
                            this.updateVoiceStatus('Playing response...');
                            source.start();
                        })
                        .catch(error => {
                            console.error('Error playing audio:', error);
                            this.updateVoiceStatus('Error playing audio response');
                        });
                        
                } catch (error) {
                    console.error('Error processing audio response:', error);
                }
            }
            
            addMessage(sender, text) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const time = new Date().toLocaleTimeString();
                messageDiv.innerHTML = `
                    <div class="message-bubble">
                        ${text}
                        <div class="message-time">${time}</div>
                    </div>
                `;
                
                this.elements.chatMessages.appendChild(messageDiv);
                this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
            }
            
            showTypingIndicator() {
                this.elements.typingIndicator.style.display = 'block';
                this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
            }
            
            hideTypingIndicator() {
                this.elements.typingIndicator.style.display = 'none';
            }
            
            updateStatus(status) {
                const indicator = this.elements.statusIndicator;
                indicator.className = `status-indicator status-${status}`;
            }
            
            updateVoiceStatus(message) {
                this.elements.voiceStatus.textContent = message;
            }
            
            showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = `Error: ${message}`;
                
                this.elements.chatMessages.appendChild(errorDiv);
                this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
                
                // Remove error after 5 seconds
                setTimeout(() => {
                    if (errorDiv.parentNode) {
                        errorDiv.parentNode.removeChild(errorDiv);
                    }
                }, 5000);
            }
        }
        
        // Initialize the chat bot when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new HybridChatBot();
        });
    </script>
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