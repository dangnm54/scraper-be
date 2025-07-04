import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional

import scraper.utils as utl
from scraper.base import run_full_flow
from scraper.config import data_folder_path


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





# ____________ define "API Endpoint" (specific URL server will respond to) ------------




# @app.get("/") means: "When someone sends a GET request to the '/' (root) address,
    # '@' -> decorator | means 'when ever someone visit' 
    # '/' -> root address
    # will run function right below the line
@app.get("/")
def read_root():
    return {"message": "Seeing this output means BE is running ok hhehe"}





@app.post("/api/run")
async def run_scraper_api(settings: ScraperSettings):
    """
    Receives scraper settings from FE and triggers scraping process.
    """
    # print(f"Received FE data: {settings.dict()}")
    print(f"Received FE data: {settings.model_dump()}")

    try:
        
        result = run_full_flow(
            file_name = settings.file_name,
            location = settings.location,
            num_guest = settings.num_guest,
            num_property = settings.num_property,
            collect_host_data = settings.collect_host_data,
            collect_booking_rate = settings.collect_booking_rate
        )
        return result

    except Exception as e:
        utl.log_error(e)
        return result





@app.get("/api/data/files", response_model=list[FileMetadata])
async def give_list_files():
    """
    Scans 'data' folder and return list of file metadata
    """

    data_path = data_folder_path
    file_list = []
    file_id = 1

    if not os.path.exists(data_path):
        return []       # return empty list if directory not exist

    for file_name in os.listdir(data_path):
        if file_name.endswith(".csv") and "full" in file_name.lower():
            file_path = os.path.join(data_path, file_name)

            # get file date
            file_date = "Unknown Date"
            try:
                # fx to extract date from filename later
                pass
            except Exception:
                timestamp = os.path.getmtime(file_path) # get modification time
                file_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

            # get item count
            item_count = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    item_count = sum(1 for line in f) - 1 # Subtract 1 for header row
                    if item_count < 0: item_count = 0
            except Exception:
                item_count = 0

            file_list.append(
                FileMetadata(
                    id = file_id,
                    file_name = file_name,
                    date_created = file_date,
                    item_count = item_count,
                    path = file_path
                )
            )
            file_id += 1

    file_list.sort(key=lambda f: f.date, reverse=True)

    return file_list



