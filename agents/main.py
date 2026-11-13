
import os
import secrets
import hmac
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field


APP_NAME = "AMIN JOON Node Agent"

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")

if len(AGENT_TOKEN) < 32:
    raise RuntimeError(
        "AGENT_TOKEN must be configured with at least 32 characters"
    )


app = FastAPI(
    title=APP_NAME,
    description="Secure node monitoring agent for AMIN JOON",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)


# ---------- Authentication ----------

def verify_agent_token(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    supplied_token = authorization[7:]

    if not hmac.compare_digest(supplied_token, AGENT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent token",
        )


# ---------- Models ----------

class PingResponse(BaseModel):
    status: str
    agent: str
    time: datetime


class AgentInfo(BaseModel):
    node_name: str = Field(min_length=2, max_length=100)
    country: str | None = None
    city: str | None = None


# ---------- Rate Limiting ----------

requests = defaultdict(deque)

def check_rate_limit(client_key: str):
    now = time.monotonic()
    window = requests[client_key]

    while window and now - window[0] > 60:
        window.popleft()

    if len(window) >= 60:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    window.append(now)


# ---------- Health ----------

@app.get("/health", response_model=PingResponse)
def health():
    return PingResponse(
        status="ok",
        agent=APP_NAME,
        time=datetime.now(timezone.utc),
    )


# ---------- Authenticated Ping ----------

@app.get("/api/v1/ping")
def authenticated_ping(
    authorization: str | None = Header(default=None),
):
    verify_agent_token(authorization)

    return {
        "status": "connected",
        "agent": APP_NAME,
        "time": datetime.now(timezone.utc).isoformat(),
    }


# ---------- Node Registration Info ----------

@app.post("/api/v1/info")
def node_info(
    data: AgentInfo,
    authorization: str | None = Header(default=None),
):
    verify_agent_token(authorization)

    return {
        "status": "received",
        "node": data.model_dump(),
    }
