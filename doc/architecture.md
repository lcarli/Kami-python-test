# Architecture — Kami Python Test

This document describes the major components of the repository and how they interact at runtime.

Components

- ai_agent_service.py

  - Responsibility: Provides an API or local service that performs higher-level AI reasoning, prompt orchestration, or agent-style behavior. This module likely accepts text or structured inputs and returns model-driven outputs.

- bot.py

  - Responsibility: Implements the conversational bot logic — message parsing, state tracking, and routing to the AI agent or other services.

- hybrid_bot.py

  - Responsibility: Orchestrates hybrid flows that combine the `bot.py` message handling with `ai_agent_service.py` logic and the `voice_live_service.py` when voice is involved. Acts as a coordinator that selects which modality or agent to call.

- voice_live_service.py

  - Responsibility: Handles microphone capture and playback, integrates with speech-to-text (STT) and text-to-speech (TTS) services or libraries. Provides a streaming interface for live voice interactions.

- start_all.py
  - Responsibility: Developer convenience script that starts the services locally (e.g., starts the voice service and bot service in separate threads/processes).

Runtime data flow (typical scenario)

1. User speaks into microphone or sends a text message.
2. `voice_live_service.py` captures audio → converts to text via STT (local or cloud) and forwards text to `hybrid_bot.py`.
3. `hybrid_bot.py` inspects message context and decides whether to call `bot.py` handlers (for simple intents) or forward to `ai_agent_service.py` for complex reasoning.
4. `ai_agent_service.py` performs processing and returns a response. The response is passed back to `hybrid_bot.py` which may send it to `bot.py` for formatting and then to `voice_live_service.py` for TTS, or directly return text to the user.

Notes and assumptions

- The repository is structured for local development and testing. Replaceable adapters (for STT/TTS or model backends) are recommended.
- Authentication, API keys, and environment configuration are kept outside source control (likely via environment variables or `config.py`). See `usage.md` for details.
