import sys
import os
import time
import logging
from typing import List, Dict, Literal, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
        'name': None,
        'title': None,
        'rating_num': None,
        'rating_star': None,
        'exp_time': None
    }

    overview_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'section.c1h2ee1b')
    log.info('Overview section found')

    name_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span.t1gpcl1t')
    name: str = name_element.text
    overview_data['name'] = name

    title_element: WebElement = overview_section.find_element(By.CSS_SELECTOR, 'span.s1h3l0w7')
    title: str = title_element.text
    overview_data['title'] = title

    try:
        rating_num_element: WebElement = overview_section.find_elements(By.CSS_SELECTOR, 'span.vqkyk4b')[0]
        log.info(f'rating_num_element: {rating_num_element.text}')
        rating_num: int = int(hst_utl.clean_string(rating_num_element.text, mode='rating_num'))
        overview_data['rating_num'] = rating_num

        rating_star_element: WebElement = overview_section.find_elements(By.CSS_SELECTOR, 'span.vqkyk4b')[1]
        rating_star: float = float(hst_utl.clean_string(rating_star_element.text, mode='rating_star'))
        overview_data['rating_star'] = round(rating_star, 2)

        # --------------------------------

        exp_num_element: WebElement = overview_section.find_elements(By.CSS_SELECTOR, 'span.vqkyk4b')[2]
        exp_num: str = exp_num_element.text

        exp_unit_element: WebElement = overview_section.find_elements(By.CSS_SELECTOR, 'span.lh1pygb')[2]
        exp_unit: str = hst_utl.clean_string(exp_unit_element.text, mode='exp_unit')

        exp_time: str = exp_num + exp_unit
        overview_data['exp_time'] = exp_time

    except NoSuchElementException as e:
        log.error('Host rating & exp data not found -> skip to next data (if any)')

    except Exception as e:
        lg.log_detail_error(e)
        log.error('Error to collect host rating & exp data -> skip to next data (if any)')

    hst_utl.pretty_dict(overview_data)
    return overview_data





def prop_data(driver: WebDriver, wait_time: float) -> Dict[str, Any]:
        
    lg.log_divider('Property data')

    prop_data: Dict[str, Any] = {
        'prop_num': None,
        'avg_prop_rv_num': None,
        'avg_prop_rv_star': None

    }

    prop_section_block: WebElement = driver.find_elements(By.CSS_SELECTOR, 'div.c1yo0219')[6]
    prop_section: WebElement = prop_section_block.find_element(By.CSS_SELECTOR, 'section')
    hst_utl.scroll_focus_element(driver, prop_section)
    log.info('Property section found')

    # --------------------------------

    tot_rv_num: int = 0
    tot_rv_star: float = 0
    tot_prop_num: int = 0
    prop_cnt: int = 0

    try:

        view_all_button_area: List[WebElement] = prop_section.find_elements(By.CSS_SELECTOR, 'div.v9765v button')

        if view_all_button_area:
            view_all_button: WebElement = view_all_button_area[0]
            tot_prop_num = int(hst_utl.clean_string(view_all_button.text, mode='prop_num'))
            prop_data['prop_num'] = tot_prop_num
            log.info(f'Found {tot_prop_num} properties')

            view_all_button.click()
            time.sleep(wait_time)
            log.info('View all button clicked')

            while prop_cnt < tot_prop_num:

                # need big screen
                prop_list: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, 'div.cy5jw6o')
                log.info(f'Pop-up has {tot_prop_num} properties')

                for prop in prop_list[prop_cnt:]:

                    prop_cnt += 1
                    lg.log_divider()

                    log.info(f'Checking property #{prop_cnt} / {tot_prop_num}')
                    hst_utl.scroll_focus_element(driver, prop)

                    prop_rv: WebElement = prop.find_element(By.CSS_SELECTOR, 'span.t1phmnpa span.a8jt5op')
                    rv_num: int = int(hst_utl.clean_string(prop_rv.text, mode='prop_num'))
                    tot_rv_num += rv_num
                    log.info(f'tot_rv_num: {tot_rv_num} (+ {rv_num})')

                    rv_star: float = float(hst_utl.clean_string(prop_rv.text, mode='rv_star'))
                    tot_rv_star += rv_star
                    log.info(f'tot_rv_star: {tot_rv_star} (+ {rv_star})')

                if prop_cnt == tot_prop_num:
                    break
                else:
                    try:
                        view_more_button: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.lk34ed1 button')
                        log.info('More button found')
                        view_more_button.click()
                        log.info('More button clicked')
                        time.sleep(wait_time)
                    except Exception as e:
                        log.error('Error finding "View more" button')
                        lg.log_detail_error(e)
                        break


        else:
            prop_list = driver.find_elements(By.CSS_SELECTOR, 'div.c3184sb')
            tot_prop_num = len(prop_list)
            prop_data['prop_num'] = tot_prop_num
            log.info(f'Carousel has {tot_prop_num} properties')

            for prop in prop_list:
                
                prop_cnt += 1
                lg.log_divider()

                log.info(f'Checking property #{prop_cnt} / {tot_prop_num}')
                hst_utl.scroll_focus_element(driver, prop)

                prop_rv_area: List[WebElement] = prop.find_elements(By.CSS_SELECTOR, 'div.sxmrbbg')

                if len(prop_rv_area) > 1:
                    prop_rv = prop_rv_area[1]

                    rv_num_element: WebElement = prop_rv.find_elements(By.CSS_SELECTOR, 'span')[7]
                    rv_num = int(hst_utl.clean_string(rv_num_element.text, mode='prop_num'))
                    tot_rv_num += rv_num
                    log.info(f'tot_rv_num: {tot_rv_num} (+ {rv_num})')

                    rv_star_element: WebElement = prop_rv.find_elements(By.CSS_SELECTOR, 'span.s1sd7v66 > span')[-1]
                    rv_star = float(hst_utl.clean_string(rv_star_element.text, mode='rating_star'))
                    tot_rv_star += rv_star
                    log.info(f'tot_rv_star: {tot_rv_star} (+ {rv_star})')

                else:
                    log.info('prop has no rating -> skip to next prop')



    except Exception as e:
        lg.log_detail_error(e)
        log.error('Error to collect property data -> skip to next prop')
        return prop_data


    if tot_prop_num > 0:
        avg_prop_rv_num: float = round(tot_rv_num / tot_prop_num, 2)
        avg_prop_rv_star: float = round(tot_rv_star / tot_prop_num, 2)
        prop_data['avg_prop_rv_num'] = avg_prop_rv_num
        prop_data['avg_prop_rv_star'] = avg_prop_rv_star
    else:
        log.error('prop_num is 0 -> skip to next prop')
        prop_data['prop_num'] = 0


    hst_utl.pretty_dict(prop_data)
    return prop_data



