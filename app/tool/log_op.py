import os
import sys
import logging
import traceback
from datetime import datetime


# -----------------------------------------------------------------------------------


# lv between INFO(20) and WARNING(30)
HEADER_LV = 25
logging.addLevelName(HEADER_LV, 'HEADER')





# logFormat inherit from parent class (logging.Formatter)
    # get all method + properties from parent class
    # LogFormat becomes logging.Formatter -> can be used like logging.Formatter
    # LogFormat inherit the __init__() from parent class
class LogFormat(logging.Formatter):

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)s | %(module)s - %(funcName)s - %(lineno)d | %(message)s',
            datefmt='%H:%M:%S'
        )

    # when log system called format(), it always provide a record object
    def format(self, record):
        
        if record.levelno == HEADER_LV:
            return record.msg
        
        # use .format() from parent class (logging.Formatter) -> internally use self.fmt and self.datefmt
        return super().format(record)





def file_run_method() -> str:
    is_server_run: bool = False

    for arg in sys.argv:
        if 'uvicorn' in arg.lower():
            is_server_run = True
            break

    if is_server_run:
        return "Server started (uvicorn)"
    else:
        return "Directly in Terminal"    





def setup_logging_for_file_directly_run() -> str:

    current_time: str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open('./app.log', 'w', encoding='utf-8') as f:
        f.write(f'LOG RECORDED AT: {current_time}\n')
        f.write(f'STARTED BY FILE: {os.path.basename(sys.argv[0])}\n')
        f.write(f'RUN METHOD: {file_run_method()}\n\n\n')


    console_handler: logging.StreamHandler = logging.StreamHandler()
    file_handler: logging.StreamHandler = logging.StreamHandler(open('./app.log', mode='a', encoding='utf-8'))


    log_format: LogFormat = LogFormat()


    # when handler recieve a log record
        # handler auto call self.formatter.format(record) (in case handler use .setFormatter())
        # this case -> LogFormat.format()
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)


    # root logger is global for entire project    
    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    log_file_path: str = os.path.abspath('./app.log')

    return log_file_path





def log_divider(ipt_message: str = '') -> None:

    if ipt_message:
        message = f'\n\n{"="*30} {ipt_message}\n'
    else:
        message = f'\n{"-"*20}\n'
    
    # same root logger created earlier (if any)
    root_logger = logging.getLogger()
    root_logger.log(HEADER_LV, message)





def log_detail_error(e: Exception) -> None:
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_traceback:

        # get full traceback
        full_traceback = traceback.format_exc()
        message = f"Full traceback:\n{full_traceback}"


        # # get 3 lastest level of error
        # traceback_info = traceback.extract_tb(exc_traceback)
        # traceback_level = 3
        # traceback_list = traceback_info[-traceback_level:]    # if requested level larger than actual list -> start from beginning of list
    
        # error_list = [str(e)]
        # for i, frame in enumerate(traceback_list):
        #     short_file_name = os.path.basename(frame.filename)
        #     frame_info = f'- Error level #{i+1}: File <{short_file_name}> | Function <{frame.name}> | Line #{frame.lineno}: {frame.line}'
        #     error_list.append(frame_info)

        # message = '\n'.join(error_list)

    else:
        message = str(e)

    root_logger = logging.getLogger()
    root_logger.error(message)




