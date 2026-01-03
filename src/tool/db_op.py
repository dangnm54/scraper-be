import os
import logging
from datetime import datetime
from typing import List, Generator
from uuid import UUID

from src.type.data import PropertyDB
import src.tool.log_op as lg


from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')



# create 'engine' and 'SessionLocal' for all functions in this file
if DATABASE_URL:
    # 'engine' -> core component connects your app to database.
    engine: Engine | None= create_engine(
        DATABASE_URL,

        # Optimized for Railway free tier
        pool_pre_ping=True,               # Test connection before using (CRITICAL)
        pool_size=2,                      # Small pool for free tier (default: 5)
        max_overflow=3,                   # Limited overflow connections
        pool_recycle=1800,                # Recycle connections after 30 min (Railway may timeout sooner)
        pool_timeout=30,                  # Wait max 30s for connection from pool
        echo_pool=False,                  # Set True only for debugging
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10,        # Connection timeout in seconds
            "keepalives": 1,              # Enable TCP keepalives
            "keepalives_idle": 30,        # Start keepalives after 30s
            "keepalives_interval": 10,    # Send keepalive every 10s
            "keepalives_count": 5         # Max 5 failed keepalives before disconnect
        }
    )

    # 'SessionLocal' -> a factory that create new database session whenever you need one.
    SessionLocal: sessionmaker | None = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine,
        expire_on_commit=False
    )

    log.info(f'Create engine and SessionLocal for database connection')

else:
    log.error("DATABASE_URL not found in .env file. Cannot connect to the database.")
    engine = None
    SessionLocal = None



# -----------------------------------------------------------------------------------



def get_db() -> Generator[Session | None, None, None]:
    """
    generator function used for FastAPI dependency injection.
    It yields a new database session for each request.
    """
    if not SessionLocal:
        log.error("Database connection not established. Cannot get database session.")
        yield None
        return

    db: Session = SessionLocal()
    log.info(f"Database session established for FastAPI request: {db}")

    try:
        yield db
    finally:
        log.info("Closing database session for FastAPI request.")
        db.close()





def create_db_session() -> Session | None:
    """
    create database session when running a file directly.
    The caller is responsible for closing this session.
    """
    if not SessionLocal:
        log.error("Database is not configured. Cannot create session.")
        return None
    
    log.info("Creating database session for direct file run.")
    
    # SessionLocal() -> create a new database session and return it to caller
    return SessionLocal()





def get_session_name(db: Session, base_name: str) -> str:
    """
    Finds a unique session name by appending a counter if the base name exists.
    e.g., "PhoCo" -> "PhoCo (1)" -> "PhoCo (2)"
    """
    # Create initial name with current date
    current_time = datetime.now().strftime('%d%m%y')
    base_session_name = f'{base_name}_{current_time}'
    
    # Query database to find all session names that start with base name
    #  '.count' -> check how many exist
    query = db.query(PropertyDB).filter(PropertyDB.session_name.like(f'{base_session_name}%'))
    count = query.count()

    if count == 0:
        return base_session_name
    else:
        return f'{base_session_name} ({count})'

