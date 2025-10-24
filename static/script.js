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
        
        // Wake word detection
        this.isWakeWordListening = false;
        this.isMicMuted = false;
        this.recognition = null;
        this.wakeWordTimeout = null;
        this.isWakeWordTriggered = false;
        this.wasVoiceActiveBeforeMute = false; // Track voice state before muting
        this.isKamiSpeaking = false; // Track when Kami is speaking to prevent echo
        
        // Voice session control - só processa áudio após wake word
        this.voiceSession = {
            active: false,           // Se a sessão está ativa
            timeout: null,           // Timer para desativar sessão
            duration: 20000,         // 20 segundos de duração
            extendOnSpeech: true,    // Estender quando detectar fala
            volumeThreshold: 0.01,   // Threshold para detectar fala
            countdownInterval: null, // Interval for countdown display
            startTime: null          // Track when session started
        };
        
        this.initializeElements();
        this.setupEventListeners();
        this.connectWebSocket();
        this.initializeWakeWordDetection();
        this.startVoiceConversation(); // Auto-start voice conversation
    }
    
    initializeElements() {
        this.elements = {
            // Main containers
            messagesArea: document.getElementById('messages-area'),
            inputContainer: document.getElementById('input-container'),
            
            // Input elements
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('send-btn'),
            
            // Voice status
            voiceStatus: document.getElementById('voice-status'),
            
            // Wake word and microphone controls
            micMuteBtn: document.getElementById('mic-mute-btn'),
            wakeWordIndicator: document.getElementById('wake-word-indicator'),
            sessionCountdown: document.getElementById('session-countdown'),
            
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
        
        // Wake word and microphone controls
        this.elements.micMuteBtn.addEventListener('click', () => this.toggleMicrophone());
        
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
            this.updateVoiceStatus('🔄 Starting voice conversation...');
            
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
                console.log('Voice WebSocket connected - waiting for wake word');
                
                // DON'T send start_conversation automatically
                // Wait for wake word detection to trigger Voice Live session
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
                const inputData = event.inputBuffer.getChannelData(0);
                
                // Calcular volume para detectar fala
                const volume = this.calculateVolume(inputData);
                
                // SÓ PROCESSA se sessão de voz estiver ativa
                // Voice Live tem echo cancellation - sempre enviar áudio
                if (this.voiceSession.active && this.voiceWs && this.voiceWs.readyState === WebSocket.OPEN) {
                    
                    // Se detectar fala (volume acima do threshold), estender sessão
                    if (volume > this.voiceSession.volumeThreshold) {
                        this.extendVoiceSession();
                    }
                    
                    // Enviar áudio para Voice Live (tem echo cancellation no backend)
                    const pcmData = this.convertToPCM16(inputData);
                    this.voiceWs.send(pcmData);
                    
                } else if (!this.voiceSession.active) {
                    // Sessão inativa - áudio ignorado
                    // console.log('Voice session inactive - audio ignored');
                }
            };
            
            // Connect audio nodes
            this.source.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            
            this.updateVoiceStatus('💬 Say "Hey, Kami" to start talking (lasts 20 seconds)');
            
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
    
    calculateVolume(float32Array) {
        // Calcula RMS (Root Mean Square) para detectar nível de fala
        let sum = 0;
        for (let i = 0; i < float32Array.length; i++) {
            sum += float32Array[i] * float32Array[i];
        }
        return Math.sqrt(sum / float32Array.length);
    }
    
    extendVoiceSession() {
        // Estende a sessão quando detectar fala
        if (this.voiceSession.active && this.voiceSession.extendOnSpeech) {
            this.setSessionTimeout();
            this.showToast('⏱️ Session extended', 'info', 2000);
            console.log('Voice session extended due to speech detection');
        }
    }
    
    activateVoiceSession() {
        // Ativar sessão de voz temporária
        this.voiceSession.active = true;
        this.voiceSession.startTime = Date.now();
        console.log('Voice session activated - Voice Live now listening');
        
        // Atualizar status visual
        this.updateVoiceStatus('💬 Say \'Hey, Kami\' to start talking (lasts 20 seconds)');
        
        // Update wake word indicator to active state
        this.elements.wakeWordIndicator.classList.add('active');
        this.elements.wakeWordIndicator.classList.remove('warning');
        
        // Start countdown display
        this.startCountdownDisplay();
        
        // Configurar timeout automático
        this.setSessionTimeout();
    }
    
    deactivateVoiceSession() {
        // Desativar sessão de voz
        this.voiceSession.active = false;
        console.log('Voice session deactivated - Voice Live stopped listening');
        
        // Limpar timeout se existir
        if (this.voiceSession.timeout) {
            clearTimeout(this.voiceSession.timeout);
            this.voiceSession.timeout = null;
        }
        
        // Stop countdown display
        this.stopCountdownDisplay();
        
        // Remove active/warning states
        this.elements.wakeWordIndicator.classList.remove('active', 'warning');
        
        // Atualizar status visual
        this.updateVoiceStatus('💬 Say "Hey, Kami" to start talking (lasts 20 seconds)');
    }
    
    startCountdownDisplay() {
        // Clear any existing countdown
        this.stopCountdownDisplay();
        
        // Show countdown element
        this.elements.sessionCountdown.classList.remove('hidden');
        
        // Track if we've shown the warning toast
        let warningShown = false;
        
        // Update countdown every 100ms for smooth display
        this.voiceSession.countdownInterval = setInterval(() => {
            if (!this.voiceSession.active || !this.voiceSession.startTime) {
                this.stopCountdownDisplay();
                return;
            }
            
            const elapsed = Date.now() - this.voiceSession.startTime;
            const remaining = Math.max(0, Math.ceil((this.voiceSession.duration - elapsed) / 1000));
            
            // Update countdown text
            this.elements.sessionCountdown.textContent = `${remaining}s`;
            
            // Show warning toast at 5 seconds
            if (remaining === 5 && !warningShown) {
                this.showToast('⏱️ Voice session ending in 5 seconds...', 'warning', 3000);
                warningShown = true;
            }
            
            // Add warning class when less than 5 seconds
            if (remaining <= 5 && remaining > 0) {
                this.elements.wakeWordIndicator.classList.add('warning');
                this.elements.wakeWordIndicator.classList.remove('active');
            } else if (remaining > 5) {
                this.elements.wakeWordIndicator.classList.add('active');
                this.elements.wakeWordIndicator.classList.remove('warning');
            }
            
            // Update status message with countdown
            if (remaining > 0) {
                this.updateVoiceStatus(`🎤 Listening... (${remaining}s remaining)`);
            }
        }, 100);
    }
    
    stopCountdownDisplay() {
        // Clear countdown interval
        if (this.voiceSession.countdownInterval) {
            clearInterval(this.voiceSession.countdownInterval);
            this.voiceSession.countdownInterval = null;
        }
        
        // Hide countdown element
        if (this.elements.sessionCountdown) {
            this.elements.sessionCountdown.classList.add('hidden');
            this.elements.sessionCountdown.textContent = '';
        }
    }
    
    setSessionTimeout() {
        // Limpar timeout anterior se existir
        if (this.voiceSession.timeout) {
            clearTimeout(this.voiceSession.timeout);
        }
        
        // Reset start time for countdown
        this.voiceSession.startTime = Date.now();
        
        // Configurar novo timeout
        this.voiceSession.timeout = setTimeout(() => {
            this.deactivateVoiceSession();
        }, this.voiceSession.duration);
        
        console.log(`Voice session timeout set for ${this.voiceSession.duration}ms`);
    }
    
    stopVoiceConversation() {
        if (!this.isVoiceActive) return;
        
        this.isVoiceActive = false;
        this.updateStatus('ready');
        this.updateVoiceStatus('Voice conversation ready');
        
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
                    this.updateVoiceStatus('✅ Voice ready! Say "Hey, Kami" to talk');
                    break;
                    
                case 'voice_live_connected':
                    this.updateVoiceStatus('✅ Connected! Say "Hey, Kami" to start');
                    break;
                    
                case 'audio_response':
                    // Handle audio response from Voice Live
                    if (data.audio_data) {
                        this.playAudioResponse(data.audio_data);
                    }
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
                    this.updateVoiceStatus('💬 Say "Hey, Kami" to start talking (lasts 20 seconds)');
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
                    
                    // Store reference to stop if interrupted
                    this.currentAudioSource = source;
                    
                    source.onended = () => {
                        this.isKamiSpeaking = false;
                        this.currentAudioSource = null;
                        this.updateStatus('listening');
                        
                        // Mostrar status baseado no estado da sessão
                        if (this.voiceSession.active) {
                            const elapsed = Date.now() - this.voiceSession.startTime;
                            const remaining = Math.max(0, Math.ceil((this.voiceSession.duration - elapsed) / 1000));
                            this.updateVoiceStatus(`🎤 Listening... (${remaining}s remaining)`);
                        } else {
                            this.updateVoiceStatus('💬 Say "Hey, Kami" to start talking (lasts 20 seconds)');
                        }
                    };
                    
                    this.isKamiSpeaking = true;
                    this.updateStatus('speaking');
                    this.updateVoiceStatus('🔊 Speaking...');
                    source.start();
                })
                .catch(error => {
                    this.isKamiSpeaking = false;
                    this.currentAudioSource = null;
                    console.error('Error playing audio:', error);
                    this.updateVoiceStatus('Error playing audio response');
                });
                
        } catch (error) {
            console.error('Error processing audio response:', error);
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
    
    // Wake word detection methods
    initializeWakeWordDetection() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported');
            this.elements.wakeWordIndicator.style.display = 'none';
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.recognition.lang = 'pt-BR';
        
        this.recognition.onresult = (event) => {
            const lastResult = event.results[event.results.length - 1];
            if (lastResult.isFinal) {
                const transcript = lastResult[0].transcript.toLowerCase().trim();
                console.log('Wake word detection:', transcript);
                
                // Melhorada detecção de wake word - mais flexível
                const wakeWords = [
                    'hey kami', 'ei kami', 'oi kami', 
                    'hey camila', 'ei camila', 'oi camila',
                    'hey kamy', 'ei kamy', 'oi kamy'
                ];
                
                const foundWakeWord = wakeWords.some(word => {
                    // Remove acentos e espaços extras para melhor matching
                    const cleanTranscript = transcript.replace(/[áàâã]/g, 'a').replace(/[éê]/g, 'e').replace(/[íî]/g, 'i');
                    return cleanTranscript.includes(word) || transcript.includes(word);
                });
                
                if (foundWakeWord) {
                    console.log('✅ Wake word detected!');
                    this.triggerWakeWord();
                }
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Wake word recognition error:', event.error);
            if (event.error === 'not-allowed') {
                this.toggleMicrophone(); // Mute if permission denied
            }
        };
        
        this.recognition.onend = () => {
            if (this.isWakeWordListening && !this.isMicMuted) {
                // Restart recognition if it stops unexpectedly
                setTimeout(() => {
                    if (this.isWakeWordListening && !this.isMicMuted) {
                        try {
                            this.recognition.start();
                        } catch (e) {
                            console.log('Recognition restart failed:', e);
                        }
                    }
                }, 1000);
            }
        };
        
        this.startWakeWordDetection();
    }
    
    startWakeWordDetection() {
        if (!this.recognition || this.isMicMuted) return;
        
        try {
            this.recognition.start();
            this.isWakeWordListening = true;
            this.updateWakeWordIndicator();
            console.log('Wake word detection started');
        } catch (e) {
            console.log('Wake word detection already running');
        }
    }
    
    stopWakeWordDetection() {
        if (!this.recognition) return;
        
        this.recognition.stop();
        this.isWakeWordListening = false;
        this.updateWakeWordIndicator();
        console.log('Wake word detection stopped');
    }
    
    toggleMicrophone() {
        this.isMicMuted = !this.isMicMuted;
        
        if (this.isMicMuted) {
            // Stop both wake word detection AND voice conversation COMPLETELY
            this.stopWakeWordDetection();
            
            // Desativar sessão de voz
            this.deactivateVoiceSession();
            
            // Store voice state to restore later
            this.wasVoiceActiveBeforeMute = this.isVoiceActive;
            
            // NEW: Send mute command to backend Voice Live service
            if (this.voiceWs && this.voiceWs.readyState === WebSocket.OPEN) {
                this.voiceWs.send(JSON.stringify({
                    'type': 'mute_voice_live',
                    'muted': true
                }));
            }
            
            // Show toast notification
            this.showToast('🔇 Microphone muted', 'info', 2000);
            
            // DON'T stop Voice Live conversation - just mute it
            // The backend will handle the muting, keep connection alive
            // if (this.isVoiceActive) {
            //     this.stopVoiceConversation();
            // }
            
            console.log('Microphone muted - all audio stopped');
            this.updateVoiceStatus('🔇 Microphone muted - click to resume');
            
        } else {
            // Resume both wake word detection AND voice conversation
            this.startWakeWordDetection();
            
            // NEW: Send unmute command to backend Voice Live service
            if (this.voiceWs && this.voiceWs.readyState === WebSocket.OPEN) {
                this.voiceWs.send(JSON.stringify({
                    'type': 'mute_voice_live',
                    'muted': false
                }));
            }
            
            // Show toast notification
            this.showToast('🔊 Microphone active - say "Hey, Kami"', 'success', 2000);
            
            // DON'T restart Voice Live conversation - it should still be connected
            // Just unmute the backend, connection should remain active
            // if (this.wasVoiceActiveBeforeMute) {
            //     setTimeout(() => {
            //         this.startVoiceConversation();
            //     }, 500);
            // }
            
            console.log('Microphone unmuted - audio resumed');
            this.updateVoiceStatus('💬 Say "Hey, Kami" to start talking (lasts 20 seconds)');
        }
        
        this.updateMicrophoneState();
        this.updateWakeWordIndicator();
    }
    
    updateMicrophoneState() {
        const micIcon = this.elements.micMuteBtn.querySelector('.mic-icon');
        const micMutedIcon = this.elements.micMuteBtn.querySelector('.mic-muted-icon');
        
        if (this.isMicMuted) {
            this.elements.micMuteBtn.classList.add('muted');
            micIcon.classList.add('hidden');
            micMutedIcon.classList.remove('hidden');
        } else {
            this.elements.micMuteBtn.classList.remove('muted');
            micIcon.classList.remove('hidden');
            micMutedIcon.classList.add('hidden');
        }
    }
    
    updateWakeWordIndicator() {
        if (this.isMicMuted) {
            this.elements.wakeWordIndicator.classList.add('muted');
            this.elements.wakeWordIndicator.classList.remove('triggered');
        } else {
            this.elements.wakeWordIndicator.classList.remove('muted');
            if (this.isWakeWordTriggered) {
                this.elements.wakeWordIndicator.classList.add('triggered');
            } else {
                this.elements.wakeWordIndicator.classList.remove('triggered');
            }
        }
    }
    
    triggerWakeWord() {
        console.log('Wake word triggered: Hey, Kami!');
        this.isWakeWordTriggered = true;
        this.updateWakeWordIndicator();
        
        // If Kami is speaking, interrupt her
        if (this.isKamiSpeaking && this.currentAudioSource) {
            console.log('Interrupting Kami - wake word detected while speaking');
            this.currentAudioSource.stop();
            this.currentAudioSource = null;
            this.isKamiSpeaking = false;
            this.showToast('🛑 Interrupted - listening now', 'info', 2000);
        } else {
            // Show toast notification for normal wake word detection
            this.showToast('Wake word detected! Starting conversation...', 'success', 2000);
        }
        
        // Send wake word detection to backend to start Voice Live
        if (this.voiceWs && this.voiceWs.readyState === WebSocket.OPEN) {
            this.voiceWs.send(JSON.stringify({
                type: 'wake_word_detected'
            }));
        }
        
        // NOVA FUNCIONALIDADE: Ativar sessão de voz
        this.activateVoiceSession();
        
        // Reset triggered state after 3 seconds
        clearTimeout(this.wakeWordTimeout);
        this.wakeWordTimeout = setTimeout(() => {
            this.isWakeWordTriggered = false;
            this.updateWakeWordIndicator();
        }, 3000);
    }
}

// Initialize the chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    new KamiChat();
});