import sys
import os
import logging
import csv
from typing import Tuple, List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions

from scraper.tool import log_op as lg
import scraper.detail_step.browser as brws
import scraper.bizfix_uat.step as step
from scraper.tool.config import wait_time, driver_path, proxy_user, proxy_password, proxy_ip, proxy_port


# -----------------------------------------------------------------------------------

if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)

web_url = 'https://maps.google.com/'
location_ipt = 'Vĩnh yên, Vĩnh phúc'
industry_ipt = 'vật liệu xây dựng'
num_data = 500



# -----------------------------------------------------------------------------------


def start_driver() -> Tuple[WebDriver | None, WebDriverWait | None]:

    extension_dir: str = brws.crt_proxy_helper_extention(proxy_user, proxy_password, proxy_ip, proxy_port)
    options_1: EdgeOptions = brws.config_basic_driver_setting()
    options_2: EdgeOptions | None = brws.config_advanced_driver_setting(extension_dir, options_1)
    

    if options_2 != None:
        driver: WebDriver | None = None
        wait: WebDriverWait | None = None
        driver, wait = brws.start_browser(driver_path, options_2)

    if driver is None and wait is None:
        log.error(f"Cannot create driver and wait")

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