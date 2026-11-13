from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AMIN JOON API",
    description="API مرکزی پنل مدیریت VPN امین جون",
    version="0.1.0",
)

# در محیط production، originها باید به دامنه‌های واقعی پنل محدود شوند.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "project": "AMIN JOON",
        "stage": "phase-0-foundation",
    }

@app.get("/", tags=["System"])
def root():
    return {
        "name": "AMIN JOON",
        "message": "به API پنل امین جون خوش آمدید",
        "docs": "/docs",
    }
