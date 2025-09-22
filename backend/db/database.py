from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure engine with connection pool and retry logic
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10,
}

# Add SQLite-specific configuration if using SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready with retry logic"""
    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            connection = engine.connect()
            connection.close()
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