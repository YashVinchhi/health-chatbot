from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import time
import logging
from ..config import settings

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the database URL from settings instead of reading directly
SQLALCHEMY_DATABASE_URL = settings.database_url

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure engine with conditional pool settings based on database type
engine_kwargs = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration (no pool settings)
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }
    logger.info("Using SQLite database configuration")
else:
    # PostgreSQL/MySQL configuration with connection pooling
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    }
    logger.info("Using PostgreSQL/MySQL database configuration with connection pooling")

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready with retry logic"""
    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            with engine.connect() as connection:
                # Test the connection using text() wrapper for SQLAlchemy 2.0 compatibility
                connection.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error("Failed to connect to database after maximum retries")
                raise
    return False

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()