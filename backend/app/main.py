
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .auth import router as auth_router
from .users import router as users_router
from .nodes import router as nodes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AMIN JOON API",
    description="API مرکزی پنل مدیریت VPN امین جون",
    version="0.3.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
