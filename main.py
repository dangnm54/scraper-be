import os
import logging
import asyncio
import sys
from starlette.responses import StreamingResponse


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional, List 


import scraper.utils as utl
import scraper.log_op as lg
import scraper.file_op as fop
from scraper.base import run_full_flow


# -------------------------------------------------------------------

lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)



# ____________  setup FastAPI app ------------------------------------------------------------

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



FE_log_stream: asyncio.Queue = asyncio.Queue()



# SSELogStream class intercepts print() and direct message to SEE queue
# worker thread use method in this class
class SSELogStream:

    def __init__(self, BE_log_stream, FE_log_stream:asyncio.Queue):
        self.BE_log_stream = BE_log_stream
        self.FE_log_stream = FE_log_stream

        # loop -> refer to main thread's event loop (event loop manage multi async tasks in thread)
        self.loop = None

    def write(self, message):
        # Write to the original stdout (e.g., the console)
        self.BE_log_stream.write(message)
        self.BE_log_stream.flush()

        # If the asyncio loop is available, also put the message in the queue for the frontend
        if self.loop and self.loop.is_running():
            for line in message.splitlines():
                if line.strip():
                    # cross-thread communication
                        # FE_log_stream -> async fx
                        # worker thread hand over '.put' to main thread
                        # a thread-safe way for worker thread to say: 
                            # I'm the worker thread
                            # and I need you (main thread) to execute this .put coroutine task for me.
                    asyncio.run_coroutine_threadsafe(
                        self.FE_log_stream.put(line.strip()), self.loop
                    )

    def flush(self):
        self.BE_log_stream.flush()



# BE_log_stream points to the original stdout (console)
BE_log_stream = sys.stdout

# every print() will go through this sse_log_stream instance
sse_log_stream = SSELogStream(BE_log_stream, FE_log_stream)
sys.stdout = sse_log_stream




# ____________ define "API Endpoint" (specific URL server will respond to) ------------


@app.get("/")
def read_root():
    return {"message": "Seeing this output means BE is running ok hhehe"}





@app.post("/api/run")
async def run_scraper_api(fe_input: ScraperSettings):
    """
    - input: data required from Fe
    - output: file in data folder
    - note:
        - trigger scraping process
        - log will be sent via SSE stream
    """

    # .get_running_loop -> get reference to the current event loop (main thread)
    # This is necessary because print() will be called from a different thread.
    if not sse_log_stream.loop:
        sse_log_stream.loop = asyncio.get_running_loop()


    # .model_dump() = .dict() | new syntax
    log.info(f"Received FE data: {fe_input.model_dump()}")     

    # .put -> adding specified string to the queue
    await FE_log_stream.put("--- Scraping started ---")

    try:
        
        # Run the synchronous, blocking function in a separate thread
        # This allows the main event loop to remain unblocked and stream logs
        result = await asyncio.to_thread(
            run_full_flow,
                file_name = fe_input.file_name,
                location = fe_input.location,
                num_guest = fe_input.num_guest,
                num_property = fe_input.num_property,
                collect_host_data = fe_input.collect_host_data,
                collect_booking_rate = fe_input.collect_booking_rate
        )

        await FE_log_stream.put('--- Scraping completed ---')
        return result

    except Exception as e:
        utl.log_error(e)
        await FE_log_stream.put('--- Scraping failed: {e} ---')
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
        file_name, file_path = fop.get_file_path(file_id).values()

        # check if file exist in server's file system
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found on path '{file_path}'.")

        return FileResponse(path=file_path, media_type='text/csv', filename=file_name)

    except HTTPException as e:
        raise e
    except Exception as e:
        utl.log_error(e)
        raise HTTPException(status_code=500, detail=f'[file-download api] Server error: {str(e)}')





# setup a contininuous connection, constantly check for new message in FE_log_stream and stream to connected client
@app.get("/sse/logs")
async def sse_logs(request:Request):
    """
    Streams server-sent events (SSE) from the FE_log_stream to connected clients.
    """
    
    async def event_generator():
        while True:

            # generator fx -> instead returning 1 value and exiting, generates sequence of values one by one, on demand.
                # - become generator function if use 'yield' keyword inside it
                # - only produce value when requested
                # - they paused execution between 'yield's
                # when run this fx, it doesn't run its code immediately, it return a 'generator object' that can be iterated
                
            if await request.is_disconnected():
                log.info('SSE client disconnected')
                log.info('-'*20)
                break

            try:
                message = await asyncio.wait_for(FE_log_stream.get(), timeout=1.0)
                yield f"data: {message}\n\n"

                FE_log_stream.task_done()
            
            except asyncio.TimeoutError:
                yield ":keep-alive\n\n"
            except Exception as e:
                utl.log_error(e)
                yield "data: Error: {e}\n\n"
                break

    # note
        # StreamingResponse -> FastAPI response class, designed for responsed where content generated overtime
        # when called event_generator() -> return a generator object that StreamingResponse can iterate over to get data
    return StreamingResponse(event_generator(), media_type="text/event-stream")

