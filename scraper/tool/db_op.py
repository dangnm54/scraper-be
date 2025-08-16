import logging
from datetime import datetime
from typing import List
from uuid import UUID


from sqlalchemy.orm import Session
from scraper.type.data import PropertyDB
from scraper.type.data import PropertyDetail

import scraper.tool.log_op as lg


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def get_session_name(db: Session, base_name: str) -> str:
    """
    Finds a unique session name by appending a counter if the base name exists.
    e.g., "PhoCo" -> "PhoCo (1)" -> "PhoCo (2)"
    """
    # Create initial name with current date
    current_time = datetime.now().strftime('%d%m%y')
    base_session_name = f'{base_name}_{current_time}'
    
    # Query database to find all session names that start with base name
    # We also use 'func.count' to check how many exist
    query = db.query(PropertyDB).filter(PropertyDB.session_name.like(f'{base_session_name}%'))
    count = query.count()

    # If no matching names are found, use the base name
    if count == 0:
        return base_session_name
    else:
        # If names already exist, create a new name with an incremented counter
        return f'{base_session_name} ({count})'



def save_data_to_db(
        detail_list: List[PropertyDetail], 
        db: Session, session_id: UUID, file_name: str,
    ) -> None:
    
    log.info(f"Saving data to db")

    if detail_list:
            
        for detail_instance in detail_list:
            try:
                db_property: PropertyDB = PropertyDB(
                    **detail_instance.model_dump(), 
                    session_id=session_id,
                    session_name=file_name
                )
                db.add(db_property)
            except Exception as e:
                lg.log_detail_error(e)
        
        db.commit()
        log.info(f"{len(detail_list)} properties saved to database.")

    else:
        log.info("No properties found to save to database")