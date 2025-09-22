#!/usr/bin/env python3
"""
Simple test script to verify backend is working
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Health Chatbot Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoints
@app.get("/")
async def root():
    return {"message": "Health Chatbot Backend is running!", "status": "ok"}

@app.get("/api/health/test")
async def test_endpoint():
    return {"message": "API connection working", "status": "success"}

@app.post("/api/health/chat")
async def simple_chat(data: dict):
    message = data.get("message", "")
    return {
        "response": f"Echo: {message}. Backend is working!",
        "intent": "test",
        "confidence": 1.0
    }

@app.get("/api/health/health-tips")
async def health_tips():
    return {
        "tips": ["Backend connection successful!", "API is responding properly"]
    }

# Serve frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    @app.get("/index.html")
    @app.get("/frontend")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/style.css")
    async def serve_css():
        return FileResponse(os.path.join(frontend_path, "style.css"))

    @app.get("/script.js")
    async def serve_js():
        return FileResponse(os.path.join(frontend_path, "script.js"))

if __name__ == "__main__":
    print("🚀 Starting Health Chatbot Backend Test Server...")
    print("📍 Frontend files:", frontend_path)
    print("🌐 Open: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
