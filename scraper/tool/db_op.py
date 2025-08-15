from datetime import datetime
from sqlalchemy.orm import Session
from scraper.type.data import PropertyDB



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