import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional, List 


import scraper.utils as utl
import scraper.file_op as fop
from scraper.base import run_full_flow


# -------------------------------------------------------------------


# ____________  setup ------------------------------------------------------------

# ____ create "FastAPI app" instance -> manages all web routes + functions
app = FastAPI()


# ____ configure CORS
# list specific origins (FE) that allowed to talk to BE
origins = [
    "http://localhost:5173",  
    # eg: http://127.0.0.1:5173",      
    # eg: "http://your-deployed-frontend.com"
]


# ____ add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,        # Allow requests from these specific origins
    allow_credentials = True,       # Allow cookies to be sent (useful for authentication later)
    allow_methods = ["*"],          # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers = ["*"]           # Allow all headers in the request
)





# ____________  define data structure for request from FE ----------------------------

class ScraperSettings(BaseModel):
    file_name: Optional[str] = None # Optional, if not defined, will be None
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


class FileDetail(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[List[dict]] = None



# ____________ define "API Endpoint" (specific URL server will respond to) ------------


@app.get("/")
def read_root():
    return {"message": "Seeing this output means BE is running ok hhehe"}





@app.post("/api/run")
async def run_scraper_api(fe_input: ScraperSettings):
    """
    Receives scraper settings from FE and triggers scraping process.
    """
    # print(f"Received FE data: {settings.dict()}")
    print(f"Received FE data: {fe_input.model_dump()}")

    try:
        
        result = run_full_flow(
            file_name = fe_input.file_name,
            location = fe_input.location,
            num_guest = fe_input.num_guest,
            num_property = fe_input.num_property,
            collect_host_data = fe_input.collect_host_data,
            collect_booking_rate = fe_input.collect_booking_rate
        )
        return result

    except Exception as e:
        utl.log_error(e)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")





@app.get("/api/data/file-list", response_model=list[FileMetadata])
async def get_file_list_api():
    try:
        file_metadata_list = fop.get_file_metadata_list()
        
        # Convert to FileMetadata objects
        file_list = [
            FileMetadata(
                id = item['id'],
                file_name = item['file_name'],
                date_created = item['date_created'],
                item_count = item['item_count'],
                path = item['path']
            )
            for item in file_metadata_list
        ]
        
        return file_list
        
    except Exception as e:
        utl.log_error(e)
        return []





@app.get("/api/data/file-detail/{file_id}", response_model=FileDetail)
async def get_file_detail_api(file_id: int):
    try:
        file_detail = fop.get_file_detail(file_id)
        return file_detail
    
    except HTTPException as e:
        raise e

    except Exception as e:
        utl.log_error(e)
        raise HTTPException(status_code=500, detail=f"[file-detail api] Server error: {str(e)}")    





@app.get("/api/data/file-download/{file_id}")
async def download_file_api(file_id: int):
    try:
        file_info = fop.get_file_path(file_id)
        file_name = file_info['file_name']
        file_path = file_info['file_path']

        # check if file exist in server's file system
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found on path '{file_path}'.")

        return FileResponse(path=file_path, media_type='text/csv', filename=file_name)

    except HTTPException as e:
        raise e
    except Exception as e:
        utl.log_error(e)
        raise HTTPException(status_code=500, detail=f'[file-download api] Server error: {str(e)}')