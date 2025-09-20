import sys
import os
import logging
import csv
from dotenv import load_dotenv
from typing import Tuple, List, Dict

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions

from src.tool import log_op as lg
from src.tool.config import wait_time
import src.detail_step.browser as brws
from src.type.data import BrowserMode

import bizfix_uat.uat_function as step

# -----------------------------------------------------------------------------------

if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)

web_url = 'https://maps.google.com/'
location_ipt = 'Vĩnh yên, Vĩnh phúc'
industry_ipt = 'vật liệu xây dựng'
num_data = 500



# -----------------------------------------------------------------------------------


# load .env file for local use
load_dotenv()

# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')

PROXY_USER: str | None = os.getenv('PROXY_USER')
PROXY_PASSWORD: str | None = os.getenv('PROXY_PASSWORD')
PROXY_IP: str | None = os.getenv('PROXY_IP')
PROXY_PORT: str | None = os.getenv('PROXY_PORT')

DRIVER_PATH: str | None = os.getenv('DRIVER_PATH')

# -----------------------------------------------------------------------------------


def start_driver() -> Tuple[WebDriver | None, WebDriverWait | None]:

    browser_mode: BrowserMode = 'local'
    log.info(f'Starting driver in <{browser_mode}> mode')


    extension_dir: str | None = None
    if PROXY_USER and PROXY_PASSWORD and PROXY_IP and PROXY_PORT:
        extension_dir = brws.crt_proxy_helper_extention(PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT)
        log.info(f"Proxy information found in.env -> driver will use proxy")
    else:
        log.warning(f"Proxy information missing in .env -> driver will not use proxy")

    
    options_1: EdgeOptions = brws.config_basic_driver_setting(browser_mode)
    options_2: EdgeOptions = brws.config_proxy_driver_setting(extension_dir, options_1)
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None

    if DRIVER_PATH:
        driver, wait = brws.start_browser(DRIVER_PATH, options_2, browser_mode)


    return driver, wait






def scrape_p1(wait_time: float, web_url: str) -> str:
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"An error in 'if driver'")
        return ''
    

    step.go_to_website(driver, wait_time, web_url)
    step.search(driver, wait_time, location_ipt, industry_ipt)
    client_list: List[Dict[str, str | None]] = step.scrape_data(driver, wait_time, num_data)

    file_path: str = step.list_dict_to_csv(client_list, 'vp_vlxd')

    return file_path




scrape_p1(wait_time, web_url)