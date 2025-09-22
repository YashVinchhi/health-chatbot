from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import logging
import os

from routers import whatsapp, sms, health_api
from db.database import engine, wait_for_db
from db import models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for database to be ready before creating tables
logger.info("Waiting for database connection...")
wait_for_db()

# Create database tables
logger.info("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

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

# Mount static files - check if frontend directory exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve the main HTML file at the root path"""
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/style.css")
    async def serve_css():
        """Serve the CSS file"""
        css_path = os.path.join(frontend_path, "style.css")
        if os.path.exists(css_path):
            return FileResponse(css_path, media_type="text/css")
        return PlainTextResponse("/* CSS file not found */", media_type="text/css")

    @app.get("/script.js")
    async def serve_js():
        """Serve the JavaScript file"""
        js_path = os.path.join(frontend_path, "script.js")
        if os.path.exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")
        return PlainTextResponse("// JS file not found", media_type="application/javascript")

    @app.get("/favicon.ico")
    async def serve_favicon():
        """Serve favicon or return empty response"""
        favicon_path = os.path.join(frontend_path, "favicon.ico")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return PlainTextResponse("", status_code=204)
else:
    @app.get("/")
    async def root():
        return {"message": "Health Chatbot API is running", "frontend_path": frontend_path}

# Metrics endpoint for Prometheus monitoring
@app.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint for Prometheus"""
    metrics = [
        "# HELP health_chatbot_requests_total Total number of requests",
        "# TYPE health_chatbot_requests_total counter",
        "health_chatbot_requests_total 1",
        "# HELP health_chatbot_up Application up status",
        "# TYPE health_chatbot_up gauge",
        "health_chatbot_up 1"
    ]
    return PlainTextResponse("\n".join(metrics), media_type="text/plain")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "health-chatbot-backend"}

# Include routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp"])
app.include_router(sms.router, prefix="/api/sms", tags=["sms"])
app.include_router(health_api.router, prefix="/api/health", tags=["health"])
