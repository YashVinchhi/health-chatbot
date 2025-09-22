from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import whatsapp, sms, health_api
from .db.database import engine
from .db import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Health Chatbot API",
    description="Backend API for Health Chatbot system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp"])
app.include_router(sms.router, prefix="/api/sms", tags=["sms"])
app.include_router(health_api.router, prefix="/api/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": "Health Chatbot API is running"}