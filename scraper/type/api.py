from typing import Dict, List, Any
from pydantic import BaseModel


# ------------------------------------------------------------------------------------------------


class ScraperSettings(BaseModel):
    file_name: str
    location: str
    num_guest: int
    num_property: int
    collect_host_data: bool = False
    collect_booking_rate: bool = False



class FileMetadata(BaseModel):
    id: str
    file_name: str
    date_created: str
    item_count: int



class FileDetail(BaseModel):
    detail: str
    data: List[Dict[str, Any]]



