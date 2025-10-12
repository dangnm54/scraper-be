import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import logging
import src.tool.log_op as lg

if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)



# -----------------------------------------------------------------------------------


# load .env file for local use
from dotenv import load_dotenv
load_dotenv()

from typing import Tuple, Dict, Any, List, cast, get_args

import pandas as pd

import src.detail_step.browser as brws
import host.host_p2 as p2

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions

from src.tool.config import wait_time
from src.type.data import BrowserMode
from host.host_type import HostDetail
import host.host_utils as hst_utl





# -----------------------------------------------------------------------------------


# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')

PROXY_USER: str | None = os.getenv('PROXY_USER')
PROXY_PASSWORD: str | None = os.getenv('PROXY_PASSWORD')
PROXY_IP: str | None = os.getenv('PROXY_IP')
PROXY_PORT: str | None = os.getenv('PROXY_PORT')

DRIVER_PATH: str | None = os.getenv('DRIVER_PATH')
LOG_FILE_PATH: str | None = os.getenv('LOG_FILE_PATH')

BROWSER_MODE_ENV: str = os.getenv('BROWSER_MODE', 'local')

if BROWSER_MODE_ENV in get_args(BrowserMode):
    BROWSER_MODE = cast(BrowserMode, BROWSER_MODE_ENV)


# -----------------------------------------------------------------------------------


def start_driver() -> Tuple[WebDriver | None, WebDriverWait | None]:

    log.info(f'Starting driver in <{BROWSER_MODE}> mode')

    extension_dir: str | None = None
    if PROXY_USER and PROXY_PASSWORD and PROXY_IP and PROXY_PORT:
        extension_dir = brws.crt_proxy_helper_extention(PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT)
        log.info(f"Proxy information found in .env -> driver will use proxy")
    else:
        log.warning(f"Proxy information missing in .env -> driver will not use proxy")

    
    options_1: EdgeOptions = brws.config_basic_driver_setting(BROWSER_MODE)
    options_2: EdgeOptions = brws.config_proxy_driver_setting(extension_dir, options_1)
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None

    if DRIVER_PATH:
        driver, wait = brws.start_browser(DRIVER_PATH, options_2, BROWSER_MODE)

    if driver != None and wait != None:
        pass
    else:
        log.error(f"Cannot create driver and wait")

    return driver, wait



def scrape_p1():

    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"Failed to start driver and create wait object")
        return []

    # --------------------------------






def scrape_p2(data_file_path: str) -> str:

    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"Failed to start driver and create wait object")
        return ''

    # --------------------------------
    
    df: pd.DataFrame = pd.read_excel(data_file_path)
    log.info(f'success convert excel file -> dataframe')

    host_list: List[Dict[str, Any]] = []
    scraped_host_cnt: int = 0
    saved_host_cnt: int = 0
    total_host_cnt: int = len(df)

    for idx, host in df.iterrows():

        scraped_host_cnt += 1
        host_name: str = str(host["name"])
        host_link: str = str(host["link"])

        lg.log_divider()
        log.info(f'Scraping host #{scraped_host_cnt + 1} / {total_host_cnt}: {host_name} - {host_link}')

        try:
            p2.go_to_website(driver, wait_time, host_link)
        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to access page of host <{host_name}> -> skip to next host')
            continue


        host_detail = HostDetail(
            name = host_name,   # str
            link = host_link,   # str

            title = None,   # str | None
            rating_num = None,   # int | None
            rating_star = None,   # float | None
            exp_time = None,   # str | None

            prop_num = None,   # int | None
            avg_prop_rv_num = None,   # float | None
            avg_prop_rv_star = None,   # float | None
        )

        try:

            overview_data: Dict[str, Any] = p2.overview_data(driver)
            for key, value in overview_data.items():
                setattr(host_detail, key, value)

            # try: 
            #     prop_data: Dict[str, Any] = p2.prop_data(driver, wait_time)
            #     for key, value in prop_data.items():
            #         setattr(host_detail, key, value)
            # except Exception as e:
            #     lg.log_detail_error(e)
            #     log.error(f'Error collect property data of host <{host_name}> -> skip to next host')
            #     continue

            hst_utl.pretty_dict(host_detail.model_dump())

            host_list.append(host_detail.model_dump())
            saved_host_cnt += 1

        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to access page of host <{host_name}> -> skip to next host')
            continue

    log.info(f'Saved {saved_host_cnt} / {scraped_host_cnt} hosts to list')

    # --------------------------------

    host_df: pd.DataFrame = pd.DataFrame(host_list)
    log.info(f'success convert list dict -> dataframe')

    host_csv_path: str = hst_utl.df_to_csv(host_df, 'host')
    log.info(f'success save dataframe to csv file: {host_csv_path}')

    return host_csv_path






# go to website
# collect each data
# add to dict
# convert dict to csv




# -----------------------------------------------------------------------------------


scrape_p2(
    # data_file_path = r"C:\Users\ADMIN\Pictures\scraper\scraper-be\data\host1.xlsx"
    data_file_path = r"C:\Users\ADMIN\Pictures\scraper\scraper-be\data\host2.xlsx"
)

