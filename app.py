import logging
import src.tool.log_op as lg

log_file_path = lg.setup_logging_for_file_directly_run()
log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------


from dotenv import load_dotenv
load_dotenv()

import os
import io
import asyncio
import pandas as pd
from typing import Dict, List, Any, cast
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pandas.core.generic import WriteExcelBuffer
from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse

import src.tool.file_op as fop
from src.base import run_full_flow
from src.tool.db_op import get_db

from src.type.api import ScraperSettings, FileMetadata, FileDetail, ResponseBody
from src.type.data import ScrapeStatus

from sqlalchemy.orm import Session
from fastapi import Depends


# ------------------------------------------------------------------------------------------------


class SSELogHandler(logging.Handler):
    def __init__(self, FE_log_stream:asyncio.Queue, loop=None):
        super().__init__()
        self.FE_log_stream = FE_log_stream

        # loop -> refer to main thread's event loop (event loop manage multi async tasks in thread)
        self.loop = loop

    def emit(self, record):
        try:
            # message = self.format(record)
            message: str = str(record.msg)

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

sse_handler: SSELogHandler = SSELogHandler(FE_log_stream)
sse_handler.setFormatter(lg.LogFormat())
sse_handler.setLevel(logging.INFO)

root_logger: logging.Logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(sse_handler)


# ------------------------------------------------------------------------------------------------


# create "FastAPI app" instance -> manages all web routes + functions
app = FastAPI()


# configure CORS
# list specific origins (FE) that allowed to talk to BE
origins: List[str] = [
    "http://localhost:5173",  
    # eg: http://127.0.0.1:5173",      
    # eg: "http://your-deployed-frontend.com"
]


# add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,        # Allow requests from these specific origins
    allow_credentials = True,       # Allow cookies to be sent (useful for authentication later)
    allow_methods = ["*"],          # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers = ["*"]           # Allow all headers in the request
)



# ------------------------------------------------------------------------------------------------


@app.get("/api/test")
def read_root() -> Dict[str, str]:
    return {"message": "Seeing this output means BE is running ok hhehe"}





@app.post("/api/run")
async def run_scraper_api(fe_input: ScraperSettings, db: Session | None = Depends(get_db)) -> JSONResponse:
    """
    - input: data required from FE
    - output: file in database
    - operation:
        - trigger scraping process
        - log will be sent via SSE stream
    """

    api_sig = '[run-scraper api]'
    
    if not db:
        log.error("Database session not found")
        error_resp = ResponseBody[None](
            success = False,
            message = f"{api_sig} Database session not found"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())

    # .get_running_loop -> get reference to the current event loop (main thread)
    if not sse_handler.loop:
        sse_handler.loop = asyncio.get_running_loop()

    current_time: str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    lg.log_divider(f"Scraping started at: {current_time}")

    log.info(f"api called: /api/run | fe_input={fe_input.model_dump()}")

    try:        
        # Run the synchronous, blocking function in a separate thread
        # This allows the main event loop to remain unblocked and stream logs
        scrape_status: ScrapeStatus = await asyncio.to_thread(
            run_full_flow,
                db,
                file_name = fe_input.file_name,
                location = fe_input.location,
                num_guest = fe_input.num_guest,
                num_property = fe_input.num_property,
                collect_host_data = fe_input.collect_host_data,
                collect_booking_rate = fe_input.collect_booking_rate
        )

        resp = ResponseBody[str](
            success = True,
            message = f"{api_sig} Finish both parts of scraping process",
            data = scrape_status.value
        )
        return JSONResponse(status_code=200, content=resp.model_dump())
        
        
    except Exception as e:
        lg.log_detail_error(e)
        await FE_log_stream.put('--- Scraping failed: {e} ---')

        error_resp = ResponseBody[List[FileMetadata]](
            success = False,
            message = f"{api_sig} Server error: {str(e)}"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())





@app.get("/api/data/file-list")
async def get_file_list_api(db: Session | None = Depends(get_db)) -> JSONResponse:
    
    api_sig = '[file-list api]'

    if not db:
        log.error("Database session not found")
        error_resp = ResponseBody[List[FileMetadata]](
            success = False,
            message = f"{api_sig} Database session not found"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())

    try:
        file_list: List[FileMetadata] = fop.get_file_list(db)

        if not file_list:
            error_resp = ResponseBody[List[FileMetadata]](
                success = False,
                message = f"{api_sig} No file found on database"
            )
            return JSONResponse(status_code=404, content=error_resp.model_dump())
            
    
        success_resp = ResponseBody[List[FileMetadata]](
            success = True,
            message = f"{api_sig} Fetch all {len(file_list)} files successfully",
            data = file_list
        )
        return JSONResponse(status_code=200, content=success_resp.model_dump())


    except Exception as e:
        lg.log_detail_error(e)
        error_resp = ResponseBody[List[FileMetadata]](
            success = False,
            message = f"{api_sig} Server error: {str(e)}"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())





@app.get("/api/data/file-detail/{file_id}")
async def get_file_detail_api(file_id: str, db: Session | None = Depends(get_db)) -> JSONResponse:
    
    api_sig = '[file-detail api]'

    if not db:
        log.error("Database session not found")
        error_resp = ResponseBody[FileDetail](
            success = False,
            message = f"{api_sig} Database session not found"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())

    try:
        file_detail: FileDetail = fop.get_file_detail(file_id, db)
        
        if not file_detail.file_data:
            error_resp = ResponseBody[FileDetail](
                success = False,
                message = f"{api_sig} File ID #{file_id} not found"
            )
            return JSONResponse(status_code=404, content=error_resp.model_dump())
        

        success_resp = ResponseBody[FileDetail](
            success = True,
            message = f"{api_sig} Fetch content for file <{file_detail.file_name}> #{file_id} successfully",
            data = file_detail
        )
        return JSONResponse(status_code=200, content=success_resp.model_dump())


    except Exception as e:
        lg.log_detail_error(e)
        error_resp = ResponseBody[FileDetail](
            success = False,
            message = f"{api_sig} Server error: {str(e)}"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())





@app.get("/api/data/file-download/{file_id}", response_model=None)
async def download_file_api(file_id: str, db: Session | None = Depends(get_db)) -> StreamingResponse | JSONResponse:

    api_sig = '[file-download api]'

    if not db:
        log.error("Database session not found")
        error_resp = ResponseBody[None](
            success = False,
            message = f"{api_sig} Database session not found"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())

    try:
        file_detail: FileDetail = fop.get_file_detail(file_id, db)

        if not file_detail.file_data:
            error_resp = ResponseBody[None](
                success = False,
                message = f"{api_sig} File ID #{file_id} not found"
            )
            return JSONResponse(status_code=404, content=error_resp.model_dump())

        file_name: str = file_detail.file_name
        file_data: List[Dict[str, Any]] = file_detail.file_data     
        file_df: pd.DataFrame = fop.list_dict_to_df(file_data)
        file_df = file_df.reset_index()

        # crt in-memory binary buffer (temporary storage) to later hold the Excel file data
        output = io.BytesIO()

        # write df to in-memory buffer as Excel file
        file_df.to_excel(cast(WriteExcelBuffer, output), index=False, engine='openpyxl')

        # seek(0) -> reset pointer to buffer's beginning -> python later read data from the start
        output.seek(0)

        response = StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

        return response

    
    except Exception as e:
        lg.log_detail_error(e)
        error_resp = ResponseBody[None](
            success = False,
            message = f"{api_sig} Server error: {str(e)}"
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())





# setup a contininuous connection, constantly check for new message in FE_log_stream and stream to connected client
@app.get("/sse/logs")
async def sse_logs(request:Request, debug:bool=False) -> StreamingResponse:
    """
    Streams server-sent events (SSE) from the FE_log_stream to connected clients.
    """

    log.info(f"api called: /sse/log | debug={debug}")
    
    async def event_generator():

        # debug = True
        if debug:
            counter: int = 0
            log.info(f"SEE endpoin in DEBUG mode")            
            
            try:
                while True:
                    if await request.is_disconnected():
                        log.info('SSE client disconnected')
                        break

                    counter += 1
                    int_message: str = f"SSE message #{counter}"
                    
                    yield f'data: {int_message}\n\n'
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                yield f"data: SSE debug stream cancelled\n\n"
            
            return



        while True:

            if await request.is_disconnected():
                log.info('SSE client disconnected')
                break

            try:
                message: str = await asyncio.wait_for(FE_log_stream.get(), timeout=1.0)
                
                sse_message: str = ''
                
                for line in message.split('\n'):
                    sse_message += f"data: {line}\n"
                
                if sse_message:
                    yield f"{sse_message}\n"

                FE_log_stream.task_done()
            
            except asyncio.TimeoutError:
                yield ":keep-alive\n\n"
            except Exception as e:
                lg.log_detail_error(e)
                yield f"[sse-logs api] data: Error: {e}\n\n"
                break

    # note
        # StreamingResponse -> FastAPI response class, designed for responsed where content generated overtime
        # when called event_generator() -> return a generator object that StreamingResponse can iterate over to get data
    return StreamingResponse(event_generator(), media_type="text/event-stream")




# test and push Docker image
