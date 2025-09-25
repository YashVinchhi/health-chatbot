from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import logging
import os

# Use try/except to handle both local and Docker imports
try:
    # Try relative imports first (for Docker)
    from .routers import whatsapp, sms, health_api
    from .db.database import engine, wait_for_db
    from .db import models
    from .config import settings
except ImportError:
    # Fall back to absolute imports (for local development)
    try:
        from backend.routers import whatsapp, sms, health_api
        from backend.db.database import engine, wait_for_db
        from backend.db import models
        from backend.config import settings
    except ImportError:
        # Last resort - direct imports
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        from routers import whatsapp, sms, health_api
        from db.database import engine, wait_for_db
        from db import models
        from config import settings

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

# Add CORS middleware - FIXED to use settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + ["*"] if settings.debug else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# FIXED: Determine frontend path more reliably
frontend_path = None
possible_frontend_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend"),  # ../frontend
    os.path.join(os.path.dirname(__file__), "frontend"),  # ./frontend
]

for path in possible_frontend_paths:
    if os.path.exists(path) and os.path.exists(os.path.join(path, "index.html")):
        frontend_path = path
        break

if frontend_path:
    # Mount static files with better error handling
    try:
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")
        logger.info(f"Frontend mounted from: {frontend_path}")
        logger.info(f"Static files available at: /static/")
    except Exception as e:
        logger.error(f"Failed to mount static files: {e}")

    @app.get("/")
    async def serve_frontend():
        """Serve the main HTML file at the root path"""
        html_path = os.path.join(frontend_path, "index.html")
        logger.info(f"Serving HTML from: {html_path}")
        if os.path.exists(html_path):
            return FileResponse(html_path)
        else:
            logger.error(f"HTML file not found at: {html_path}")
            return PlainTextResponse("Frontend not found", status_code=404)

    @app.get("/style.css")
    async def serve_css():
        """Serve the CSS file with proper headers"""
        css_path = os.path.join(frontend_path, "style.css")
        logger.info(f"CSS requested - serving from: {css_path}")
        logger.info(f"CSS file exists: {os.path.exists(css_path)}")

        if os.path.exists(css_path):
            logger.info(f"CSS file size: {os.path.getsize(css_path)} bytes")
            # Read the CSS content and ensure it's valid
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                logger.info(f"CSS content length: {len(css_content)} characters")
                logger.info(f"CSS starts with: {css_content[:100]}")

                # Return CSS with explicit headers
                response = PlainTextResponse(
                    css_content,
                    media_type="text/css",
                    headers={
                        "Content-Type": "text/css; charset=utf-8",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )
                logger.info("CSS served successfully with proper headers")
                return response
            except Exception as e:
                logger.error(f"Error reading CSS file: {e}")
                return PlainTextResponse("/* Error loading CSS */", media_type="text/css", status_code=500)
        else:
            logger.error(f"CSS file not found at: {css_path}")
            return PlainTextResponse("/* CSS file not found */", media_type="text/css", status_code=404)

    @app.get("/script.js")
    async def serve_js():
        """Serve the JavaScript file"""
        js_path = os.path.join(frontend_path, "script.js")
        logger.info(f"JS requested - serving from: {js_path}")
        logger.info(f"JS file exists: {os.path.exists(js_path)}")
        if os.path.exists(js_path):
            logger.info(f"JS file size: {os.path.getsize(js_path)} bytes")
            return FileResponse(js_path, media_type="application/javascript", headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Type": "application/javascript; charset=utf-8"
            })
        else:
            logger.error(f"JS file not found at: {js_path}")
            return PlainTextResponse("// JS file not found", media_type="application/javascript", status_code=404)

    # Additional static file routes for common assets
    @app.get("/static/{file_path:path}")
    async def serve_static_files(file_path: str):
        """Serve static files from frontend directory"""
        file_full_path = os.path.join(frontend_path, file_path)
        logger.info(f"Static file requested: {file_path} -> {file_full_path}")

        if os.path.exists(file_full_path) and os.path.isfile(file_full_path):
            # Determine content type based on file extension
            content_type = "text/plain"
            if file_path.endswith('.css'):
                content_type = "text/css"
            elif file_path.endswith('.js'):
                content_type = "application/javascript"
            elif file_path.endswith('.html'):
                content_type = "text/html"
            elif file_path.endswith(('.png', '.jpg', '.jpeg')):
                content_type = "image/*"
            elif file_path.endswith('.ico'):
                content_type = "image/x-icon"

            return FileResponse(file_full_path, media_type=content_type)
        else:
            logger.error(f"Static file not found: {file_full_path}")
            return PlainTextResponse("File not found", status_code=404)

    @app.get("/favicon.ico")
    async def serve_favicon():
        """Serve favicon or return empty response"""
        favicon_path = os.path.join(frontend_path, "favicon.ico")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        return PlainTextResponse("", status_code=204)
else:
    logger.warning("Frontend not found, serving API only")
    @app.get("/")
    async def root():
        return {
            "message": "Health Chatbot API is running",
            "status": "API Only - Frontend not found",
            "api_docs": "/docs"
        }

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
