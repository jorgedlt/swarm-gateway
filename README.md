# Swarm Gateway

The Swarm Gateway provides a secure HTTP interface for AI agents and external processes to interact with the Swarm ecosystem. It translates HTTP requests into NATS messages and relays responses back via HTTP, serving as the communication relay between external interfaces and the internal NATS messaging fabric.

## Purpose

- Expose a clean, secure HTTP API for AI agents
- Translate HTTP requests to NATS messages for internal pod communication
- Relay NATS responses back as HTTP responses
- Maintain compatibility with message patterns from Cron, Vault, and other agents
- Ensure safe, predictable, and easy-to-work-with interface

## Dependencies

- NATS server (swarm-natscore) for message routing
- Relies on other pods for specific services (e.g., swarm-vaultctl for credentials, swarm-cronctl for scheduling)

## Interfaces

### HTTP Endpoints

- `POST /send/{target}`: Generic endpoint to send messages to any NATS subject `swarm.{target}`
  - Headers: `X-API-Key` (required if API_KEY env var is set)
  - Body: `{"message": "string", "timeout": 30}`
  - Response: `{"response": "string"}`

- `POST /cron/trigger`: Send trigger requests to swarm-cronctl
  - Headers: `X-API-Key`
  - Body: `{"schedule": "cron_expression", "action": "action_name", "timeout": 30}`
  - Maps to NATS: `swarm.cron` with message `trigger:{schedule}:{action}`

- `POST /vault/request`: Request credentials from swarm-vaultctl
  - Headers: `X-API-Key`
  - Body: `{"resource": "resource_name", "scope": "read|write|admin", "timeout": 30}`
  - Maps to NATS: `swarm.vault` with message `request:{resource}:{scope}`

### NATS Subjects

- Publishes requests to `swarm.{target}` (e.g., `swarm.cron`, `swarm.vault`)
- Specific mappings: `/cron/trigger` -> `swarm.cron`, `/vault/request` -> `swarm.vault`
- Expects responses via NATS request-reply pattern

## Message Patterns

- Requests: JSON-encoded strings sent to NATS
- Responses: JSON-encoded strings returned via HTTP
- Error handling: HTTP status codes (401 for auth, 504 for timeout, 500 for NATS errors)

## Operational State

- Connects to NATS on startup at `nats://localhost:4222` (configurable via env)
- Runs FastAPI server on port 8000
- Requires API_KEY env var for authentication (optional)

## Assumptions

- NATS server is running and accessible
- Target pods are subscribed to their respective subjects
- Messages are UTF-8 encoded strings
- Timeouts are handled gracefully

## Build and Run

### Standalone
```bash
docker build -t swarm-gateway .
docker run -e API_KEY=yourkey -p 8000:8000 swarm-gateway
```

### Full Swarm Integration
Use the provided `docker-compose.yml` to deploy the entire Swarm system:
```bash
docker-compose up --build
```
This starts all pods (natscore, logger, gateway, vaultctl, cronctl, shepard) with proper networking and dependencies.