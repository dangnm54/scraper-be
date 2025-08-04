from typing import Dict, List, Any, Hashable
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
    id: int
    file_name: str
    date_created: str
    item_count: int
    path: str



# pandas creates dictionaries with Hashable keys
class FileDetail(BaseModel):
    detail: str
    data: List[Dict[Hashable, Any]] | None



