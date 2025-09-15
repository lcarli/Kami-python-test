#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import asyncio
import io
import json
import logging
from typing import Optional

try:
    import azure.cognitiveservices.speech as speechsdk
    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    logging.warning("Azure Speech SDK not available. Voice features will be disabled.")

from config import DefaultConfig

class VoiceService:
    """
    Service for handling Azure Speech Service integration including
    speech-to-text and text-to-speech functionality.
    """
    
    def __init__(self, config: DefaultConfig):
        self.config = config
        self.speech_config = None
        self.audio_config = None
        self.is_configured = False
        
        if SPEECH_SDK_AVAILABLE and config.SPEECH_KEY and config.SPEECH_REGION:
            self._initialize_speech_service()
    
    def _initialize_speech_service(self):
        """Initialize Azure Speech Service configuration."""
        try:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.config.SPEECH_KEY,
                region=self.config.SPEECH_REGION
            )
            
            # Set default language
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.speech_synthesis_language = "en-US"
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            self.is_configured = True
            logging.info("Azure Speech Service initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure Speech Service: {e}")
            self.is_configured = False
    
    def is_available(self) -> bool:
        """Check if voice services are available and configured."""
        return SPEECH_SDK_AVAILABLE and self.is_configured
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """
        Convert speech audio data to text using Azure Speech Service.
        
        Args:
            audio_data: Raw audio bytes (WAV format expected)
            
        Returns:
            Recognized text or None if recognition fails
        """
        if not self.is_available():
            logging.warning("Speech-to-text not available: service not configured")
            return None
        
        try:
            # Create audio stream from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Push audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logging.info(f"Speech recognized: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logging.warning("No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logging.error(f"Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logging.error(f"Error details: {cancellation_details.error_details}")
                return None
                
        except Exception as e:
            logging.error(f"Speech-to-text error: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech audio using Azure Speech Service.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes (WAV format) or None if synthesis fails
        """
        if not self.is_available():
            logging.warning("Text-to-speech not available: service not configured")
            return None
        
        try:
            # Create synthesizer with default audio config (in-memory stream)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # This will return audio data in memory
            )
            
            # Perform synthesis
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logging.info(f"Text-to-speech completed for text: {text[:50]}...")
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logging.error(f"Error details: {cancellation_details.error_details}")
                return None
                
        except Exception as e:
            logging.error(f"Text-to-speech error: {e}")
            return None
    
    def get_supported_voices(self) -> list:
        """
        Get list of supported voices for speech synthesis.
        
        Returns:
            List of voice information or empty list if not available
        """
        if not self.is_available():
            return []
        
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )
            
            voices_result = synthesizer.get_voices_async().get()
            
            if voices_result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices_info = []
                for voice in voices_result.voices:
                    voices_info.append({
                        'name': voice.name,
                        'display_name': voice.display_name,
                        'local_name': voice.local_name,
                        'gender': str(voice.gender),
                        'locale': voice.locale
                    })
                return voices_info
            else:
                logging.error("Failed to retrieve voices list")
                return []
                
        except Exception as e:
            logging.error(f"Error getting supported voices: {e}")
            return []

class VoiceLiveAgent:
    """
    Voice Live Agent implementation for real-time voice interactions.
    Based on Azure AI Speech Service Voice Live Agents functionality.
    """
    
    def __init__(self, voice_service: VoiceService):
        self.voice_service = voice_service
        self.is_active = False
        
    async def start_voice_session(self):
        """Start a voice live session."""
        if not self.voice_service.is_available():
            raise Exception("Voice service not available")
        
        self.is_active = True
        logging.info("Voice live session started")
    
    async def stop_voice_session(self):
        """Stop the voice live session."""
        self.is_active = False
        logging.info("Voice live session stopped")
    
    async def process_voice_input(self, audio_data: bytes) -> Optional[str]:
        """
        Process voice input and return the response text.
        
        Args:
            audio_data: Raw audio bytes from user
            
        Returns:
            Response text or None if processing fails
        """
        if not self.is_active:
            logging.warning("Voice session not active")
            return None
        
        # Convert speech to text
        user_text = await self.voice_service.speech_to_text(audio_data)
        
        if user_text:
            # For now, echo the recognized text
            # In a real implementation, this would be processed by the bot logic
            response_text = f"I heard you say: {user_text}"
            return response_text
        
        return None
    
    async def get_voice_response(self, response_text: str) -> Optional[bytes]:
        """
        Get voice response for the given text.
        
        Args:
            response_text: Text to convert to speech
            
        Returns:
            Audio bytes or None if synthesis fails
        """
        if not self.is_active:
            logging.warning("Voice session not active")
            return None
        
        return await self.voice_service.text_to_speech(response_text)