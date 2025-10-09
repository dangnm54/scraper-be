from math import ceil
import time
import logging
from typing import List, Dict, Literal, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import host.host_utils as hst_utl
import src.tool.log_op as lg


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def go_to_website(driver: WebDriver, wait_time: float, website_url: str) -> None:

    lg.log_divider('Go to website')

    try:
        driver.get(website_url)
        log.info(f'Go to website: {website_url}')
        
        try:
            driver.find_element(By.CSS_SELECTOR, 'section.c1ip518t')
            log.info('Page loaded properly')
        except:
            log.info('Page not loaded properly, refreshing...')
            driver.refresh()
            time.sleep(wait_time)

        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)



def overview_data(driver: WebDriver) -> Dict[str, Any]:
    
    lg.log_divider('Overview data')

    overview_data: Dict[str, Any] = {
        'title': None,
        'rating_star': None,
        'rating_num': None,
        'exp_time': None
    }

    overview_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'section.c1h2ee1b')
    log.info('Overview section found')
    
    title_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span.s1h3l0w7')
    title: str = title_element.text
    overview_data['title'] = title

    rating_star_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span[data-testid="Đánh giá-stat-heading"]')
    rating_star: int = int(rating_star_element.text)
    overview_data['rating_star'] = rating_star

    rating_num_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span[data-testid="Xếp hạng-stat-heading"]')
    rating_num: str = hst_utl.clean_string(rating_num_element.text, mode='rating_num')
    overview_data['rating_num'] = int(rating_num)

    exp_num_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span[data-testid="Tháng kinh nghiệm đón tiếp khách-stat-heading"]')
    exp_num: str = exp_num_element.text
    exp_unit_element: WebElement = overview_section.find_elements(By.CSS_SELECTOR, 'span.lh1pygb')[2]
    exp_unit: str = hst_utl.clean_string(exp_unit_element.text, mode='exp_unit')
    exp_time: str = exp_num + exp_unit
    overview_data['exp_time'] = exp_time

    hst_utl.pretty_dict(overview_data)
    return overview_data



def prop_data(driver: WebDriver, wait: WebDriverWait) -> Dict[str, Any]:
        
    lg.log_divider('Property data')

    prop_data: Dict[str, Any] = {
        'prop_num': None,
        'avg_prop_rv_star': None,
        'avg_prop_rv_num': None
    }

    prop_section: WebElement = driver.find_elements(By.CSS_SELECTOR, 'div.c1yo0219')[6]
    log.info('Property section found')

    


    hst_utl.pretty_dict(prop_data)
    return prop_data