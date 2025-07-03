import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional

import scraper.utils as utl
from scraper.base import run_full_flow


# -------------------------------------------------------------------


# ____________ Create "FastAPI app" instance -> manages all web routes + functions
app = FastAPI()


# ____________ Configure CORS
# list specific origins (FE) that allowed to talk to BE
origins = [
    "http://localhost:5173",  
    # eg: http://127.0.0.1:5173",      
    # eg: "http://your-deployed-frontend.com"
]


# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,        # Allow requests from these specific origins
    allow_credentials = True,       # Allow cookies to be sent (useful for authentication later)
    allow_methods = ["*"],          # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers = ["*"]           # Allow all headers in the request
)


# define data structure for request from FE
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


# ____________ Define "API Endpoint" (specific URL server will respond to)


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



# @app.get("/") means: "When someone sends a GET request to the '/' (root) address,
    # '@' -> decorator | means 'when ever someone visit' 
    # '/' -> root address
    # will run function right below the line
@app.get("/")
def read_root():
    return {"message": "Seeing this output means BE is running ok hhehe"}
