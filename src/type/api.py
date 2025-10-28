from typing import Dict, List, Any, TypeVar, Generic
from pydantic import BaseModel


# ------------------------------------------------------------------------------------------------


class ScraperSettings(BaseModel):
    file_name: str
    location_url: str
    num_guest: int | None
    num_property: int
    collect_host_data: bool = False
    collect_booking_rate: bool = False



class FileMetadata(BaseModel):
    id: str
    file_name: str
    item_count: int
    date_created: str



class FileDetail(BaseModel):
    file_name: str
    file_data: List[Dict[str, Any]]



class DeleteAllInput(BaseModel):
    password: str



class DeleteAllResult(BaseModel):
    deleted_file_cnt: int
    deleted_row_cnt: int



T = TypeVar('T')
class ResponseBody(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None
