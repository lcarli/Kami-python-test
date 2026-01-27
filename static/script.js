/**
 * Kami Chat Assistant - Modern JavaScript Client
 * Handles text chat and voice conversation
 */

class KamiChat {
    constructor() {
        this.ws = null;
        this.voiceWs = null;
        this.isVoiceActive = false;
        this.isConnected = false;
        this.isVoiceSessionActive = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.connectWebSocket();
    }
    
    initializeElements() {
        this.elements = {
            // Main containers
            messagesArea: document.getElementById('messages-area'),
            inputContainer: document.getElementById('input-container'),
            
            // Input elements
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('send-btn'),
            
            // Voice controls
            voiceLiveBtn: document.getElementById('voice-live-btn'),
            voiceSessionIndicator: document.getElementById('voice-session-indicator'),
            sessionCountdown: document.getElementById('session-countdown'),
            voiceStatus: document.getElementById('voice-status'),
            
            // Status and indicators
            statusIndicator: document.getElementById('status-indicator'),
            typingIndicator: document.getElementById('typing-indicator'),
            toastContainer: document.getElementById('toast-container')
        };
    }
    
    setupEventListeners() {
        // Text input controls
        this.elements.sendBtn.addEventListener('click', () => this.sendTextMessage());
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendTextMessage();
            }
        });
        
        // Voice Live button
        if (this.elements.voiceLiveBtn) {
            this.elements.voiceLiveBtn.addEventListener('click', () => this.toggleVoiceLive());
        }
        
        // Auto-resize input
        this.elements.messageInput.addEventListener('input', () => this.autoResizeInput());
    }
    
    autoResizeInput() {
        const input = this.elements.messageInput;
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateStatus('ready', 'Ready');
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateStatus('error', 'Disconnected');
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error', 'Connection Error');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'text_response':
                this.addMessage('assistant', data.message);
                this.hideTypingIndicator();
                break;
            case 'voice_status':
                this.updateVoiceStatus(data.status);
                break;
            case 'error':
                this.showError(data.message);
                this.hideTypingIndicator();
                break;
        }
    }
    
    async sendTextMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        this.elements.messageInput.value = '';
        this.autoResizeInput();
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
                this.addMessage('assistant', data.response);
            } else {
                this.showError(data.error || 'Failed to send message');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            this.hideTypingIndicator();
        }
    }
    
    async startVoiceConversation() {
        if (this.isVoiceActive) return;
        
        try {
            this.updateStatus('listening');
            this.isVoiceActive = true;
            this.isVoiceSessionActive = true;
            this.updateVoiceStatus('🔄 Connecting to Voice Live...');
            this.updateVoiceButton(true);
            
            // Connect to voice WebSocket (audio is captured server-side by Voice Live API)
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const voiceWsUrl = `${protocol}//${window.location.host}/api/voice/ws`;
            
            this.voiceWs = new WebSocket(voiceWsUrl);
            
            this.voiceWs.onopen = () => {
                console.log('Voice WebSocket connected');
                
                // Send start command - Voice Live API will capture audio from server microphone
                this.voiceWs.send(JSON.stringify({
                    type: 'start_voice_session'
                }));
                
                this.updateVoiceStatus('🎤 Voice active - speak now!');
                this.showToast('🎤 Voice activated!', 'success', 2000);
            };
            
            this.voiceWs.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleVoiceMessage(data);
            };
            
            this.voiceWs.onclose = () => {
                this.updateVoiceStatus('Voice conversation ended');
                console.log('Voice WebSocket disconnected');
                this.isVoiceActive = false;
                this.isVoiceSessionActive = false;
                this.updateVoiceButton(false);
            };
            
            this.voiceWs.onerror = (error) => {
                console.error('Voice WebSocket error:', error);
                this.showError('Voice connection error');
                this.isVoiceActive = false;
                this.isVoiceSessionActive = false;
                this.updateVoiceButton(false);
            };
            
            console.log('Voice conversation started - audio captured by Voice Live API');
            
        } catch (error) {
            this.showError('Failed to start voice: ' + error.message);
            this.stopVoiceConversation();
        }
    }
    
    toggleVoiceLive() {
        if (this.isVoiceSessionActive) {
            this.stopVoiceConversation();
            this.showToast('🔇 Voice stopped', 'info', 2000);
        } else {
            this.startVoiceConversation();
        }
    }
    
    updateVoiceButton(active) {
        const btn = this.elements.voiceLiveBtn;
        if (!btn) return;
        
        const text = btn.querySelector('.voice-btn-text');
        const indicator = this.elements.voiceSessionIndicator;
        
        if (active) {
            btn.classList.add('active');
            if (text) text.textContent = 'Stop Voice';
            if (indicator) indicator.classList.remove('hidden');
        } else {
            btn.classList.remove('active');
            if (text) text.textContent = 'Start Voice';
            if (indicator) indicator.classList.add('hidden');
        }
    }
    
    stopVoiceConversation() {
        if (!this.isVoiceActive) return;
        
        this.isVoiceActive = false;
        this.isVoiceSessionActive = false;
        this.updateStatus('ready');
        this.updateVoiceStatus('Click the voice button to start');
        this.updateVoiceButton(false);
        
        // Close voice WebSocket and notify server to stop Voice Live
        if (this.voiceWs) {
            if (this.voiceWs.readyState === WebSocket.OPEN) {
                this.voiceWs.send(JSON.stringify({
                    'type': 'stop_conversation'
                }));
            }
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
                    this.updateVoiceStatus('✅ Voice ready! Speak now...');
                    break;
                    
                case 'voice_live_connected':
                    this.updateVoiceStatus('✅ Connected! Speak now...');
                    break;
                    
                case 'audio_response':
                    // Audio is played server-side by Voice Live API
                    console.log('Audio response received (played on server)');
                    break;
                    
                case 'transcript':
                    // Handle transcript from Voice Live - AUDIO ONLY MODE
                    // Do NOT add to chat - voice conversations are audio-only
                    if (data.text) {
                        console.log('User voice input (not shown in chat):', data.text);
                        this.updateVoiceStatus('🤔 Thinking...');
                    }
                    break;
                    
                case 'response_text':
                    // Handle text response from Voice Live - AUDIO ONLY MODE
                    // Do NOT add to chat - voice conversations are audio-only
                    if (data.text) {
                        console.log('Agent text response (not shown in chat):', data.text);
                    }
                    break;
                    
                case 'conversation_ended':
                    this.updateVoiceStatus('Voice Live conversation ended');
                    this.stopVoiceConversation();
                    break;
                    
                case 'error':
                    this.showError('Voice Live error: ' + (data.message || 'Unknown error'));
                    break;
                
                case 'status':
                    // Handle status messages from Voice Live
                    console.log('Voice Live status:', data.message || 'Status update');
                    break;
                    
                case 'session_created':
                    // Handle session creation confirmation
                    console.log('Voice Live session created:', data.session_id || 'Session active');
                    this.updateVoiceStatus('🎤 Listening...');
                    break;
                    
                case 'speech_started':
                    // Handle speech detection
                    console.log('Speech started detected by Voice Live');
                    break;
                    
                case 'audio_transcript':
                    // Handle audio transcript from Voice Live (agent speech)
                    console.log('Agent audio transcript:', data.text || 'Audio generated');
                    break;
                    
                case 'mute_status':
                    // Handle mute confirmation from backend
                    console.log('Mute status confirmed:', data.muted ? 'muted' : 'unmuted');
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
    
    addMessage(sender, text) {
        // Create message group if this is the first message or sender changed
        let messageGroup = this.elements.messagesArea.lastElementChild;
        
        if (!messageGroup || !messageGroup.classList.contains('message-group') ||
            messageGroup.dataset.sender !== sender) {
            messageGroup = document.createElement('div');
            messageGroup.className = 'message-group';
            messageGroup.dataset.sender = sender;
            this.elements.messagesArea.appendChild(messageGroup);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(text)}</p>
                <time class="message-time">${time}</time>
            </div>
        `;
        
        messageGroup.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        this.elements.messagesArea.scrollTop = this.elements.messagesArea.scrollHeight;
    }
    
    showTypingIndicator() {
        this.elements.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.elements.typingIndicator.classList.add('hidden');
    }
    
    updateStatus(status, text) {
        const statusText = this.elements.statusIndicator.querySelector('.status-text');
        const statusDot = this.elements.statusIndicator.querySelector('.status-dot');
        
        if (statusText) statusText.textContent = text;
        
        // Update status dot color based on status
        statusDot.style.background = status === 'ready' ? '#22c55e' : 
                                   status === 'listening' ? '#3b82f6' :
                                   status === 'error' ? '#ef4444' : '#94a3b8';
    }
    
    updateVoiceStatus(message) {
        this.elements.voiceStatus.textContent = message;
    }
    
    showError(message) {
        // Create error message group
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant';
        errorDiv.innerHTML = `
            <div class="message-content" style="background: #fee2e2; color: #dc2626; border: 1px solid #fecaca;">
                <p>⚠️ ${this.escapeHtml(message)}</p>
                <time class="message-time">${new Date().toLocaleTimeString([], {
                    hour: '2-digit', 
                    minute: '2-digit'
                })}</time>
            </div>
        `;
        
        messageGroup.appendChild(errorDiv);
        this.elements.messagesArea.appendChild(messageGroup);
        this.scrollToBottom();
        
        // Remove error after 5 seconds
        setTimeout(() => {
            if (messageGroup.parentNode) {
                messageGroup.remove();
            }
        }, 5000);
    }
    
    // Toast notification system
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Icon based on type
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
            <span class="toast-message">${this.escapeHtml(message)}</span>
            <span class="toast-close">×</span>
        `;
        
        // Add to container
        this.elements.toastContainer.appendChild(toast);
        
        // Click to dismiss
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.dismissToast(toast);
        });
        
        // Click anywhere on toast to dismiss
        toast.addEventListener('click', () => {
            this.dismissToast(toast);
        });
        
        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                this.dismissToast(toast);
            }, duration);
        }
        
        return toast;
    }
    
    dismissToast(toast) {
        if (!toast || !toast.parentNode) return;
        
        toast.classList.add('toast-out');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300); // Match animation duration
    }
}

// Initialize the chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    new KamiChat();
});