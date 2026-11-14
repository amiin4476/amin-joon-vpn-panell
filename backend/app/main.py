
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .users import router as users_router
from .nodes import router as nodes_router
from .node_security import get_node_fernet
from .config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate encryption and application settings before startup.
    get_node_fernet()
    get_settings()
    yield


app = FastAPI(
    title="AMIN JOON API",
    description="API مرکزی پنل مدیریت VPN امین جون",
    version="0.4.0",
    lifespan=lifespan,
)


settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(nodes_router)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "project": "AMIN JOON",
        "stage": "phase-2-node-management",
    }


@app.get("/", tags=["System"])
def root():
    return {
        "name": "AMIN JOON",
        "message": "به API پنل امین جون خوش آمدید",
        "docs": "/docs",
    }
