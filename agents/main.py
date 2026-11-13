
import os
import hmac
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

import psutil
from fastapi import FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field


APP_NAME = "AMIN JOON Node Agent"
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")
NODE_NAME = os.getenv("NODE_NAME", "unknown-node")

if len(AGENT_TOKEN) < 32:
    raise RuntimeError(
        "AGENT_TOKEN must contain at least 32 characters"
    )


app = FastAPI(
    title=APP_NAME,
    version="0.3.0",
    docs_url=None,
    redoc_url=None,
)

requests = defaultdict(deque)


def authenticate(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = authorization[7:]

    if not hmac.compare_digest(token, AGENT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent token",
        )


def check_rate_limit(client_ip: str):
    now = time.monotonic()
    window = requests[client_ip]

    while window and now - window[0] > 60:
        window.popleft()

    if len(window) >= 60:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    window.append(now)


def protect_request(request: Request, authorization: str | None):
    authenticate(authorization)

    check_rate_limit(
        request.client.host if request.client else "unknown"
    )


class AgentInfo(BaseModel):
    node_name: str = Field(min_length=2, max_length=100)
    country: str | None = None
    city: str | None = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": APP_NAME,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/ping")
def ping(
    request: Request,
    authorization: str | None = Header(default=None),
):
    protect_request(request, authorization)

    return {
        "status": "connected",
        "node": NODE_NAME,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/metrics")
def metrics(
    request: Request,
    authorization: str | None = Header(default=None),
):
    protect_request(request, authorization)

    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_cores = psutil.cpu_count()

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "node": NODE_NAME,

        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,

        "cpu": {
            "percent": cpu_percent,
            "cores": cpu_cores,
        },

        "memory": {
            "total_bytes": memory.total,
            "used_bytes": memory.used,
            "percent": memory.percent,
        },

        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "percent": disk.percent,
        },

        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/info")
def node_info(
    data: AgentInfo,
    request: Request,
    authorization: str | None = Header(default=None),
):
    protect_request(request, authorization)

    return {
        "status": "received",
        "node": data.model_dump(),
    }
