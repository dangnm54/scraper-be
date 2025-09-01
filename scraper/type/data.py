from typing import Literal,Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from .__init__ import Base  # Import the Base we just created


# ------------------------------------------------------------------------------------------------

class ScrapeStatus(Enum):
    success = 'finish both scrape_p1 and scrape_p2'
    failed = 'failed in scrape_p1'
    partial = 'finish only scrape_p1, failed in scrape_p2'


# SQLAlchemy model
# This class represents 'properties' table in Supabase
class PropertyDB(Base):
    __tablename__ = "properties"

    # columns definition for database table
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    session_id = Column(PG_UUID(as_uuid=True), index=True, default=uuid4)
    session_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prop_code = Column(String, index=True)
    prop_name = Column(String)
    prop_link = Column(String)

    scrape_result = Column(String)

    guest_num = Column(Integer)
    bed_num = Column(Integer)
    bath_num = Column(Integer)
    location = Column(String)
    ggmap_link = Column(String)

    rating_title = Column(String)
    rating_star = Column(Float)
    rating_num = Column(Integer)

    host_name = Column(String)
    host_title = Column(String)
    host_rating_star = Column(Float)
    host_rating_num = Column(Integer)
    host_exp = Column(String)
    host_link = Column(String)
    
    this_month_booked_rate = Column(Float)
    next_1_month_booked_rate = Column(Float)
    next_3_month_booked_rate = Column(Float)



ScrapeResult = Literal['Success', 'Failed', 'Partial']

# Pydantic model for API input/output
class PropertyDetail(BaseModel):
    # overview_data
    id: UUID = Field(default_factory=uuid4)
    prop_code: str
    prop_name: str
    prop_link: str
    scrape_result: ScrapeResult

    guest_num: Optional[int] = None
    bed_num: Optional[int] = None
    bath_num: Optional[int] = None
    location: Optional[str] = None


    # rating_data
    rating_title: Optional[str] = None
    rating_star: Optional[float] = None
    rating_num: Optional[int] = None


    # host_data 
    host_name: Optional[str] = None
    host_title: Optional[str] = None
    host_rating_star: Optional[float] = None
    host_rating_num: Optional[int] = None
    host_exp: Optional[str] = None
    host_link: Optional[str] = None


    # booking_rate_data 
    this_month_booked_rate: Optional[float] = None
    next_1_month_booked_rate: Optional[float] = None
    next_3_month_booked_rate: Optional[float] = None


    # tells Pydantic to work with SQLAlchemy objects
    class Config:
        from_attributes = True



    # deffered -------------------------------------------------------
    # ___utility_data___
        # Utility_num: Optional[int] = None,
        # Utility_bathroom: Optional[int] = None
        # Utility_bedroom: Optional[List[str]] = None
        # Utility_entertain: Optional[List[str]] = None
        # Utility_safety: Optional[List[str]] = None
        # Utility_kitchen: Optional[List[str]] = None
        # Utility_outdoor: Optional[List[str]] = None
        # Utility_parking: Optional[List[str]] = None
        # Utility_service: Optional[List[str]] = None
        # Utility_not_included: Optional[List[str]] = None

    # ___rating_data___
        # Rating_clean_score: Optional[float] = None
        # Rating_accuracy_score: Optional[float] = None
        # Rating_checkin_score: Optional[float] = None
        # Rating_commu_score: Optional[float] = None
        # Rating_location_score: Optional[float] = None
        # Rating_value_score: Optional[float] = None

    # ___co-host_data___
        # Co_host_num: Optional[int] = None
        # Co_host_name: Optional[List[str]] = None
        # Co_host_link: Optional[List[str]] = None

    # ___booking_rate_data___
        # Last_1_month_booked_rate: Optional[float] = None
        # Last_3_month_booked_rate: Optional[float] = None






