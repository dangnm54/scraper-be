import logging
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
        self.fmt = '%(asctime)s | %(levelname)s | %(module)s - %(funcName)s - %(lineno)d | %(message)s'
        self.datefmt = '%Y-%m-%d %H:%M:%S'
        super().__init__(self.fmt, self.datefmt)


    # when log system called format(), it always provide a record object
    def format(self, record):
        
        if record.levelno == HEADER_LV:
            if record.msg:
                return f'\n\n{"="*30} {record.msg}\n'
            else:
                return f'\n{"-"*60}\n'
        

        # use .format() from parent class (logging.Formatter) -> internally use self.fmt and self.datefmt
        return super().format(record)





def setup_logging_for_file_directly_run():

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open('./app.log', 'w') as f:
        f.write(f'LOG RECORDED AT: {current_time}\n')


    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('./app.log', mode='a')
    
    log_format = LogFormat()


    # when handler recieve a log record
        # handler auto call self.formatter.format(record) (in case handler use .setFormatter())
        # this case -> LogFormat.format()
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # root logger is global for entire project    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)





def log_divider(log_message=''):

    # same root logger created earlier (if any)
    root_logger = logging.getLogger()
    root_logger.log(HEADER_LV, log_message)
