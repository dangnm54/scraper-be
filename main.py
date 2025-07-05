import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional

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





# ____________ define "API Endpoint" (specific URL server will respond to) ------------


# ___Lesson
    # GET  
    #     URL parameter is src of truth -> define available parameter
    #     Fx receive what URL provide
    # POST
    #     Fx  parameter is src of truth -> define what API expect
    #     URL has no parameter
    #     request body (JSON) is validated against the Fx parameter type



# @app.get("/") means: "When someone sends a GET request to the '/' (root) address,
    # '@' -> decorator | means 'when ever someone visit' 
    # '/' -> root address
    # will run function right below the line
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
async def get_file_list():
    """
    Scans 'data' folder and return list of file metadata
    """
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




@app.get("/api/data/file-detail/{file_id}")
async def get_file_detail(file_id: int):
    """
    Fetches content of specific file by ID.
    Reads CSV, convert to list of dict, return to FE
    """

    try:
        file_metadata_list = fop.get_file_metadata_list()
        file_path = None
        file_name = None

        for item in file_metadata_list:
            if item['id'] == file_id:
                file_path = item['path']
                file_name = item['file_name']
                break

        if not file_path:   
            # file_path is None -> not None is true -> raise 404
            raise HTTPException(status_code=404, detail=f"File ID {file_id} not found.")
        

        # read csv content
        detail_df = fop.csv_to_df(file_path, mode=2)
        
            # orient -> dictate the struc of dict
            # 'records' -> 'list of dict' structure 
        detail_dict = detail_df.to_dict(orient='records') 

        return {
            "status": "success",
            "message": f'Content for {file_name} fetched successfully',
            "data": detail_dict
        }


    except Exception as e:
        utl.log_error(e)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")