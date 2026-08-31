"""
App instance and router mounting only. No business logic, no endpoint
definitions — those live in each module's router.py.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.generations.router import router as generations_router

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Gracefully close shared HTTP clients on shutdown.
    from app.ai.client import http_client as ai_http
    from app.images.client import http_client as img_http
    await ai_http.aclose()
    await img_http.aclose()


app = FastAPI(title="The Quiet Authority — Social Generator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

app.include_router(generations_router)

# Mount the static files for uploads
os.makedirs("uploads/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}
