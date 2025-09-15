"""
Azure Voice Live API Service
Real-time voice agent integration with Azure AI Foundry
Based on Microsoft's official Voice Live quickstart documentation
"""

import os
import uuid
import json
import time
import base64
import logging
import threading
import numpy as np
import sounddevice as sd
import queue
import signal
import sys
from collections import deque
from dotenv import load_dotenv
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from typing import Dict, Union, Literal, Set
from typing_extensions import Iterator, TypedDict, Required
import websocket
from websocket import WebSocketApp
from datetime import datetime

# Global variables for thread coordination
stop_event = threading.Event()
connection_queue = queue.Queue()

# Audio configuration
AUDIO_SAMPLE_RATE = 24000

logger = logging.getLogger(__name__)

class VoiceLiveConnection:
    """WebSocket connection handler for Voice Live API"""
    
    def __init__(self, url: str, headers: dict) -> None:
        self._url = url
        self._headers = headers
        self._ws = None
        self._message_queue = queue.Queue()
        self._connected = False

    def connect(self) -> None:
        """Establish WebSocket connection"""
        def on_message(ws, message):
            self._message_queue.put(message)

        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket connection closed")
            self._connected = False

        def on_open(ws):
            logger.info("WebSocket connection opened")
            self._connected = True

        self._ws = websocket.WebSocketApp(
            self._url,
            header=self._headers,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Start WebSocket in a separate thread
        self._ws_thread = threading.Thread(target=self._ws.run_forever)
        self._ws_thread.daemon = True
        self._ws_thread.start()

        # Wait for connection to be established
        timeout = 10  # seconds
        start_time = time.time()
        while not self._connected and time.time() - start_time < timeout:
            time.sleep(0.1)

        if not self._connected:
            raise ConnectionError("Failed to establish WebSocket connection")

    def recv(self) -> str:
        """Receive message from WebSocket"""
        try:
            return self._message_queue.get(timeout=1)
        except queue.Empty:
            return None

    def send(self, message: str) -> None:
        """Send message to WebSocket"""
        if self._ws and self._connected:
            self._ws.send(message)

    def close(self) -> None:
        """Close WebSocket connection"""
        if self._ws:
            self._ws.close()
            self._connected = False

class AzureVoiceLive:
    """Azure Voice Live API client"""
    
    def __init__(
        self,
        *,
        azure_endpoint: str | None = None,
        api_version: str | None = None,
        token: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._azure_endpoint = azure_endpoint
        self._api_version = api_version
        self._token = token
        self._api_key = api_key
        self._connection = None

    def connect(self, project_name: str, agent_id: str, agent_access_token: str) -> VoiceLiveConnection:
        """Connect to Voice Live API"""
        if self._connection is not None:
            raise ValueError("Already connected to the Voice Live API.")
        if not project_name:
            raise ValueError("Project name is required.")
        if not agent_id:
            raise ValueError("Agent ID is required.")
        if not agent_access_token:
            raise ValueError("Agent access token is required.")

        azure_ws_endpoint = self._azure_endpoint.rstrip('/').replace("https://", "wss://")

        url = f"{azure_ws_endpoint}/voice-live/realtime?api-version={self._api_version}&agent-project-name={project_name}&agent-id={agent_id}&agent-access-token={agent_access_token}"

        auth_header = {"Authorization": f"Bearer {self._token}"} if self._token else {"api-key": self._api_key}
        request_id = uuid.uuid4()
        headers = {"x-ms-client-request-id": str(request_id), **auth_header}

        self._connection = VoiceLiveConnection(url, headers)
        self._connection.connect()
        return self._connection

class AudioPlayerAsync:
    """Asynchronous audio player for real-time playback"""
    
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.stream = sd.OutputStream(
            callback=self.callback,
            samplerate=AUDIO_SAMPLE_RATE,
            channels=1,
            dtype=np.int16,
            blocksize=2400,
        )
        self.playing = False

    def callback(self, outdata, frames, time, status):
        """Audio callback for sounddevice"""
        if status:
            logger.warning(f"Stream status: {status}")
        with self.lock:
            data = np.empty(0, dtype=np.int16)
            while len(data) < frames and len(self.queue) > 0:
                item = self.queue.popleft()
                frames_needed = frames - len(data)
                data = np.concatenate((data, item[:frames_needed]))
                if len(item) > frames_needed:
                    self.queue.appendleft(item[frames_needed:])
            if len(data) < frames:
                data = np.concatenate((data, np.zeros(frames - len(data), dtype=np.int16)))
        outdata[:] = data.reshape(-1, 1)

    def add_data(self, data: bytes):
        """Add audio data to playback queue"""
        with self.lock:
            np_data = np.frombuffer(data, dtype=np.int16)
            self.queue.append(np_data)
            if not self.playing and len(self.queue) > 0:
                self.start()

    def start(self):
        """Start audio playback"""
        if not self.playing:
            self.playing = True
            self.stream.start()

    def stop(self):
        """Stop audio playback"""
        with self.lock:
            self.queue.clear()
        self.playing = False
        self.stream.stop()

    def terminate(self):
        """Terminate audio stream"""
        with self.lock:
            self.queue.clear()
        self.stream.stop()
        self.stream.close()

class VoiceLiveService:
    """Voice Live service manager"""
    
    def __init__(self, callback_handler=None):
        self.callback_handler = callback_handler
        self.client = None
        self.connection = None
        self.audio_player = None
        self.threads = []
        self.running = False
        
        # Load configuration
        load_dotenv("./.env", override=True)
        self.endpoint = os.environ.get("AZURE_VOICE_LIVE_ENDPOINT")
        self.agent_id = os.environ.get("AI_FOUNDRY_AGENT_ID")
        self.project_name = os.environ.get("AI_FOUNDRY_PROJECT_NAME")
        self.api_version = os.environ.get("AZURE_VOICE_LIVE_API_VERSION", "2025-05-01-preview")
        self.api_key = os.environ.get("AZURE_VOICE_LIVE_API_KEY")

    def start_session(self):
        """Start a Voice Live session"""
        try:
            # Initialize authentication
            credential = DefaultAzureCredential()
            scopes = "https://ai.azure.com/.default"
            token = credential.get_token(scopes)

            # Create client
            self.client = AzureVoiceLive(
                azure_endpoint=self.endpoint,
                api_version=self.api_version,
                token=token.token,
                # api_key=self.api_key,  # Use token instead
            )

            # Connect to Voice Live API
            self.connection = self.client.connect(
                project_name=self.project_name,
                agent_id=self.agent_id,
                agent_access_token=token.token
            )

            # Configure session
            session_update = {
                "type": "session.update",
                "session": {
                    "turn_detection": {
                        "type": "azure_semantic_vad",
                        "threshold": 0.3,
                        "prefix_padding_ms": 200,
                        "silence_duration_ms": 200,
                        "remove_filler_words": False,
                        "end_of_utterance_detection": {
                            "model": "semantic_detection_v1",
                            "threshold": 0.01,
                            "timeout": 2,
                        },
                    },
                    "input_audio_noise_reduction": {
                        "type": "azure_deep_noise_suppression"
                    },
                    "input_audio_echo_cancellation": {
                        "type": "server_echo_cancellation"
                    },
                    "voice": {
                        "name": "en-US-Ava:DragonHDLatestNeural",
                        "type": "azure-standard",
                        "temperature": 0.8,
                    },
                },
                "event_id": ""
            }
            
            self.connection.send(json.dumps(session_update))
            logger.info("Voice Live session started")
            
            if self.callback_handler:
                self.callback_handler("session_started", {"config": session_update})

            # Initialize audio player
            self.audio_player = AudioPlayerAsync()
            
            # Start threads
            self.running = True
            stop_event.clear()
            
            send_thread = threading.Thread(target=self._listen_and_send_audio)
            receive_thread = threading.Thread(target=self._receive_audio_and_playback)
            
            send_thread.start()
            receive_thread.start()
            
            self.threads = [send_thread, receive_thread]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Voice Live session: {e}")
            if self.callback_handler:
                self.callback_handler("error", {"message": str(e)})
            return False

    def stop_session(self):
        """Stop the Voice Live session"""
        try:
            self.running = False
            stop_event.set()
            
            # Wait for threads to finish
            for thread in self.threads:
                thread.join(timeout=2)
            
            # Clean up audio
            if self.audio_player:
                self.audio_player.terminate()
            
            # Close connection
            if self.connection:
                self.connection.close()
                
            logger.info("Voice Live session stopped")
            
            if self.callback_handler:
                self.callback_handler("session_stopped", {})
                
        except Exception as e:
            logger.error(f"Error stopping Voice Live session: {e}")

    def _listen_and_send_audio(self):
        """Listen to microphone and send audio to Voice Live API"""
        logger.info("Starting audio stream...")
        
        stream = sd.InputStream(channels=1, samplerate=AUDIO_SAMPLE_RATE, dtype="int16")
        try:
            stream.start()
            read_size = int(AUDIO_SAMPLE_RATE * 0.02)
            while not stop_event.is_set() and self.running:
                if stream.read_available >= read_size:
                    data, _ = stream.read(read_size)
                    audio = base64.b64encode(data).decode("utf-8")
                    param = {"type": "input_audio_buffer.append", "audio": audio, "event_id": ""}
                    data_json = json.dumps(param)
                    if self.connection:
                        self.connection.send(data_json)
                else:
                    time.sleep(0.001)
                    
        except Exception as e:
            logger.error(f"Audio stream interrupted: {e}")
        finally:
            stream.stop()
            stream.close()
            logger.info("Audio stream closed")

    def _receive_audio_and_playback(self):
        """Receive audio from Voice Live API and play it back"""
        last_audio_item_id = None
        
        logger.info("Starting audio playback...")
        try:
            while not stop_event.is_set() and self.running:
                raw_event = self.connection.recv() if self.connection else None
                if raw_event is None:
                    continue

                try:
                    event = json.loads(raw_event)
                    event_type = event.get("type")
                    
                    logger.debug(f"Received event: {event_type}")

                    if event_type == "session.created":
                        session = event.get("session")
                        logger.info(f"Session created: {session.get('id')}")
                        if self.callback_handler:
                            self.callback_handler("session_created", {"session_id": session.get('id')})

                    elif event_type == "conversation.item.input_audio_transcription.completed":
                        user_transcript = event.get("transcript", "")
                        logger.info(f"User input: {user_transcript}")
                        if self.callback_handler:
                            self.callback_handler("user_transcript", {"text": user_transcript})

                    elif event_type == "response.text.done":
                        agent_text = event.get("text", "")
                        logger.info(f"Agent text response: {agent_text}")
                        if self.callback_handler:
                            self.callback_handler("agent_text", {"text": agent_text})

                    elif event_type == "response.audio_transcript.done":
                        agent_audio = event.get("transcript", "")
                        logger.info(f"Agent audio response: {agent_audio}")
                        if self.callback_handler:
                            self.callback_handler("agent_audio_transcript", {"text": agent_audio})

                    elif event_type == "response.audio.delta":
                        if event.get("item_id") != last_audio_item_id:
                            last_audio_item_id = event.get("item_id")

                        bytes_data = base64.b64decode(event.get("delta", ""))
                        if bytes_data and self.audio_player:
                            self.audio_player.add_data(bytes_data)

                    elif event_type == "input_audio_buffer.speech_started":
                        logger.info("Speech started")
                        if self.audio_player:
                            self.audio_player.stop()
                        if self.callback_handler:
                            self.callback_handler("speech_started", {})

                    elif event_type == "error":
                        error_details = event.get("error", {})
                        error_type = error_details.get("type", "Unknown")
                        error_code = error_details.get("code", "Unknown")
                        error_message = error_details.get("message", "No message provided")
                        error_msg = f"Error received: Type={error_type}, Code={error_code}, Message={error_message}"
                        logger.error(error_msg)
                        if self.callback_handler:
                            self.callback_handler("error", {"message": error_msg})
                            
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON event: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in audio playback: {e}")
        finally:
            if self.audio_player:
                self.audio_player.terminate()
            logger.info("Playback done")

def write_conversation_log(message: str, log_folder: str = "logs") -> None:
    """Write a message to the conversation log"""
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfilename = f"{timestamp}_voice_live_conversation.log"
    
    with open(f'{log_folder}/{logfilename}', 'a') as conversation_log:
        conversation_log.write(message + "\n")

# Main execution for standalone testing
if __name__ == "__main__":
    def test_callback(event_type, data):
        """Test callback handler"""
        print(f"Event: {event_type}, Data: {data}")
        if event_type in ["user_transcript", "agent_text", "agent_audio_transcript"]:
            write_conversation_log(f"{event_type}: {data.get('text', '')}")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    )
    
    # Create and start service
    service = VoiceLiveService(callback_handler=test_callback)
    
    try:
        if service.start_session():
            print("Voice Live session started. Press 'q' and Enter to quit.")
            while True:
                user_input = input()
                if user_input.strip().lower() == 'q':
                    break
        else:
            print("Failed to start Voice Live session")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        service.stop_session()
        print("Voice Live session ended")