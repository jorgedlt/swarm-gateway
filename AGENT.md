# Swarm Gateway Agent

## Role

The Swarm Gateway agent acts as the HTTP interface for AI agents in the Swarm ecosystem. It translates incoming HTTP requests into NATS messages, forwards them to appropriate internal pods (e.g., Cron, Vault), and relays responses back via HTTP. Its primary focus is providing a secure, predictable, and clean communication bridge between external AIs and the internal NATS fabric.

## Directory Structure

- `app.py`: Main FastAPI application with HTTP endpoints and NATS integration
- `requirements.txt`: Python dependencies (FastAPI, NATS client, etc.)
- `Dockerfile`: Container build instructions using Python slim base
- `README.md`: Project documentation, setup, and usage
- `AGENT.md`: This file, detailing agent role and operations
- `.gitignore`: Excludes sensitive files and build artifacts

## Operational Notes

- **Startup**: Connects to NATS at `nats://localhost:4222` on app launch
- **Security**: Requires `API_KEY` environment variable for HTTP auth via `X-API-Key` header
- **Endpoints**: Generic `/send/{target}` and specific `/cron/trigger`, `/vault/request`
- **Message Patterns**: Sends UTF-8 encoded strings to NATS subjects like `swarm.cron`, expects JSON responses
- **Dependencies**: Relies on swarm-natscore for messaging, swarm-cronctl and swarm-vaultctl for services
- **Assumptions**: NATS server running, target pods subscribed, messages are valid strings
- **Maintenance**: Rebuild container after code changes, ensure NATS connectivity for functionality

## Continuity

If restarted or redeployed, refer to README.md for setup and this file for role clarity. Maintain message compatibility with peer agents to ensure ecosystem stability.