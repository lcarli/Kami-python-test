/**
 * Kami Hybrid Chat Bot - JavaScript Client
 * Handles text chat and voice live conversation
 */

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