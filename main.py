import os
import logging
import asyncio
from datetime import datetime
from starlette.responses import StreamingResponse


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional, List 


import scraper.tool.log_op as lg
import scraper.detail_step.file_op as fop
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


class SSELogHandler(logging.Handler):
    def __init__(self, FE_log_stream:asyncio.Queue, loop=None):
        super().__init__()
        self.FE_log_stream = FE_log_stream

        # loop -> refer to main thread's event loop (event loop manage multi async tasks in thread)
        self.loop = loop

    def emit(self, record):
        try:
            # message = self.format(record)
            message = record.msg

            if record.levelno == lg.HEADER_LV:
                message += '\n'

            # If the asyncio loop is available, also put the message in the queue for the frontend
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.FE_log_stream.put(message), self.loop
                )
        except Exception as e:
            lg.log_detail_error(e)



FE_log_stream: asyncio.Queue = asyncio.Queue()

sse_handler = SSELogHandler(FE_log_stream)
sse_handler.setFormatter(lg.LogFormat())
sse_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.addHandler(sse_handler)




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
    if not sse_handler.loop:
        sse_handler.loop = asyncio.get_running_loop()

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    lg.log_divider(f"Scraping started at: {current_time}")

    log.info(f"api called: /api/run | fe_input={fe_input.model_dump()}")

    log.info(f"Received FE data: {fe_input.model_dump()}")     

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

        return result

    except Exception as e:
        lg.log_detail_error(e)
        await FE_log_stream.put('--- Scraping failed: {e} ---')
        raise HTTPException(status_code=500, detail=f"[run-scraper api] Server error: {str(e)}")






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
        lg.log_detail_error(e)
        return []





@app.get("/api/data/file-detail/{file_id}", response_model=FileDetail)
async def get_file_detail_api(file_id: int):
    try:
        file_detail = fop.get_file_detail(file_id)
        return file_detail
    
    except HTTPException as e:
        raise e

    except Exception as e:
        lg.log_detail_error(e)
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
        lg.log_detail_error(e)
        raise HTTPException(status_code=500, detail=f'[file-download api] Server error: {str(e)}')





# setup a contininuous connection, constantly check for new message in FE_log_stream and stream to connected client
@app.get("/sse/logs")
async def sse_logs(request:Request, debug:bool=False):
    """
    Streams server-sent events (SSE) from the FE_log_stream to connected clients.
    """

    log.info(f"api called: /sse/log | debug={debug}")
    
    async def event_generator():

        # debug = True
        if debug:
            counter = 0
            log.info(f"SEE endpoin in DEBUG mode")            
            
            try:
                while True:
                    if await request.is_disconnected():
                        log.info('SSE client disconnected')
                        break

                    counter += 1
                    int_message = (f"SSE message #{counter}")
                    
                    yield f'data: {int_message}\n\n'
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                yield "data: SSE debug stream cancelled\n\n"
            
            return



        while True:

            if await request.is_disconnected():
                log.info('SSE client disconnected')
                break

            try:
                message = await asyncio.wait_for(FE_log_stream.get(), timeout=1.0)
                
                sse_message = ""
                
                for line in message.split('\n'):
                    sse_message += f"data: {line}\n"
                
                if sse_message:
                    yield f"{sse_message}\n"

                FE_log_stream.task_done()
            
            except asyncio.TimeoutError:
                yield ":keep-alive\n\n"
            except Exception as e:
                lg.log_detail_error(e)
                yield "[sse-logs api] data: Error: {e}\n\n"
                break

    # note
        # StreamingResponse -> FastAPI response class, designed for responsed where content generated overtime
        # when called event_generator() -> return a generator object that StreamingResponse can iterate over to get data
    return StreamingResponse(event_generator(), media_type="text/event-stream")

