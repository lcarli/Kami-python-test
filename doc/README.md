# Kami Python Test — Documentation

This `doc/` folder contains human-readable documentation for the Kami Python Test project. It explains the purpose of the repository, how the main components interact, how to run the code locally on Windows PowerShell, and links to authoritative Microsoft documentation where appropriate.

Files in this folder:

- `README.md` — This overview file.
- `architecture.md` — Component diagram, responsibilities, and data flow.
- `usage.md` — Setup, configuration, and run instructions for Windows PowerShell.
- `microsoft_references.md` — Curated links to official Microsoft documentation used by or relevant to this project.

Quick summary of repository purpose

- The code integrates a conversational bot with AI services (an agent service and hybrid bot orchestration). It includes a voice service for live audio interactions, an AI agent service that performs reasoning or model orchestration, and entrypoint scripts to start the services.

Primary files and responsibilities (high-level):

- `ai_agent_service.py` — Hosts or orchestrates AI model interactions and agent logic.
- `bot.py` — Core bot logic for message handling and routing.
- `hybrid_bot.py` — Integrates different modalities (text + voice or agent + bot) into a hybrid conversation flow.
- `voice_live_service.py` — Real-time voice capture and playback; interfaces with speech recognition/synthesis services.
- `start_all.py` — Convenience script to start all services together (development use).

See `architecture.md` for a component diagram and `usage.md` for setup and commands.

Maintainers: See `README.md` in the project root for authorship.
