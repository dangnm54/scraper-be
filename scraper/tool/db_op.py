import os
import logging
from datetime import datetime
from typing import List, Generator
from uuid import UUID

from scraper.type.data import PropertyDB, PropertyDetail
import scraper.tool.log_op as lg

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


# load .env file
load_dotenv()

# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')


# create 'engine' and 'SessionLocal' for all functions in this file
if DATABASE_URL:
    # 'engine' -> core component connects your app to database.
    engine: Engine | None= create_engine(DATABASE_URL)

    # 'SessionLocal' -> a factory that create new database session whenever you need one.
    SessionLocal: sessionmaker | None = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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





# def save_data_to_db(
#         detail_list: List[PropertyDetail], 
#         db: Session, session_id: UUID, file_name: str,
#     ) -> None:
    
#     log.info(f"Saving data to db")

#     if detail_list:
            
#         for detail_instance in detail_list:
#             try:
#                 db_property: PropertyDB = PropertyDB(
#                     **detail_instance.model_dump(), 
#                     session_id = session_id,
#                     session_name = file_name
#                 )
#                 db.add(db_property)

#             except Exception as e:
#                 lg.log_detail_error(e)
        
#         db.commit()
#         log.info(f"{len(detail_list)} properties saved to database.")

#     else:
#         log.info("No properties found to save to database")