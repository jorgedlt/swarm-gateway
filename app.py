from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import asyncio
import nats
from nats.aio.client import Client as NATS
import os

app = FastAPI(title="Swarm Gateway", description="HTTP to NATS bridge for AI agents")

class MessageRequest(BaseModel):
    message: str
    timeout: int = 30  # seconds

class CronTriggerRequest(BaseModel):
    schedule: str  # e.g., "*/5 * * * *" for cron expression
    action: str
    timeout: int = 30

class VaultRequest(BaseModel):
    resource: str  # e.g., "database", "api"
    scope: str = "read"  # read, write, admin
    timeout: int = 30

nc: NATS | None = None

@app.on_event("startup")
async def startup_event():
    global nc
    nc = await nats.connect("nats://localhost:4222")  # Adjust NATS URL as needed

@app.on_event("shutdown")
async def shutdown_event():
    if nc:
        await nc.close()

@app.post("/send/{target}")
async def send_message(target: str, request: MessageRequest, x_api_key: str = Header(None)):
    api_key = os.getenv("API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not nc:
        raise HTTPException(status_code=500, detail="NATS connection not available")

    subject = f"swarm.{target}"
    try:
        response = await nc.request(subject, request.message.encode(), timeout=request.timeout)
        return {"response": response.data.decode()}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NATS error: {str(e)}")

@app.post("/cron/trigger")
async def trigger_cron(request: CronTriggerRequest, x_api_key: str = Header(None)):
    api_key = os.getenv("API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not nc:
        raise HTTPException(status_code=500, detail="NATS connection not available")

    message = f"trigger:{request.schedule}:{request.action}"
    try:
        response = await nc.request("swarm.cron", message.encode(), timeout=request.timeout)
        return {"response": response.data.decode()}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NATS error: {str(e)}")

@app.post("/vault/request")
async def request_vault(request: VaultRequest, x_api_key: str = Header(None)):
    api_key = os.getenv("API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not nc:
        raise HTTPException(status_code=500, detail="NATS connection not available")

    message = f"request:{request.resource}:{request.scope}"
    try:
        response = await nc.request("swarm.vault", message.encode(), timeout=request.timeout)
        return {"response": response.data.decode()}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NATS error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)