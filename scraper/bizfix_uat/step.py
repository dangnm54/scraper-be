import logging
import time
from typing import List, Dict

import scraper.tool.log_op as lg

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


# -----------------------------------------------------------------------------------

log = logging.getLogger(__name__)

def go_to_website(driver: WebDriver, wait_time: int, web_url: str) -> None:

    lg.log_divider('Go to website')

    try:
        driver.get(web_url)
        log.info(f'Go to website: {web_url}')
        time.sleep(wait_time)

    except Exception as e:
        log.error(f"An error in 'go_to_website': {e}")





def search(driver: WebDriver, wait_time: int, location_ipt: str, industry_ipt: str) -> None:

    lg.log_divider('Search')

    try:
        search_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'input.searchboxinput')
        search_element.send_keys(location_ipt, Keys.ENTER)

        time.sleep(wait_time)

        search_element.send_keys(industry_ipt, Keys.ENTER)
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)





def scrape_data(driver: WebDriver, wait_time: int, num_data: int) -> None:

    lg.log_divider('Scrape data')

    try:
        result_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb[role="feed"]')
        result_list: List[WebElement] = result_section.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')

        for client in result_list:

            client_data: Dict[str, str] = {
                'name': '',
                'address': '',
                'phone': '',
                'ggmap_link': ''
            }

            client.click()
            detail_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.bJzME.Hu9e2e')

            name_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'span.a5H0ec')
            name: str = name_element.text

            phone_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'button.CsEnBe[data-tooltip="Copy phone number"]')
            if phone_element:
                phone_num_element: WebElement = phone_element.find_element(By.CSS_SELECTOR, 'div.Io6YTe')
                phone: str = phone_num_element.text
            else:
                phone = ''
            
            
            




    except Exception as e:
        lg.log_detail_error(e)
