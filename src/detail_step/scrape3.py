from email.charset import QP
import time
import logging
from typing import Dict, Any, List, Tuple, cast

from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

import src.tool.log_op as lg
import src.tool.utils as utl
import src.tool.get_ipt as ipt


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def book_rate_info(driver: WebDriver, wait_time: float) -> Dict[str, Any]:
    """
    operation: control 2 functions:
        - detail_booking_cal -> count num of total days and booked days in a month
        - final_stage_book_cal -> calculate book rate
    """

    lg.log_divider('Book rate info')

    book_rate_data: Dict[str, Any] = {
        'this_month_booked_rate': None,  # Optional[float]
        'next_1_month_booked_rate': None,  # Optional[float]
        'next_3_month_booked_rate': None,  # Optional[float]
    }

    month_data: Dict[str, Any] = ipt.get_date_for_book_data()

    try:

        calender_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.c1e8f4ze')
        utl.scroll_focus_element(driver, calender_section)
        log.info('Calender section found')

        time.sleep(wait_time)
        lg.log_divider()

        # --------------------------------

        # month_data: Dict[str, Any] = {
        #     'this_month': 0, # int
        #     'next_1_month': 0, # int
        #     'next_3_month': [], # List[int]
        # }

        # --------------------------------

        for key, month in month_data.items():

            book_rate: float | None = None

            if type(month) == int:

                # continue
                target_month: int = month
                log.info(f'_____Target month: {target_month}_____')

                tot_day: int = 0
                booked_day: int = 0
                tot_day, booked_day = book_rate_cnt(driver, wait_time, target_month)

                book_rate = book_rate_cal(booked_day, tot_day)

            # --------------------------------

            elif type(month) == list:

                target_month_range: List[int] = month
                log.info(f'_____Target month_list: {target_month_range}_____')

                all_tot_day: int = 0
                all_booked_day: int = 0

                # --------------------------------

                for target_month in target_month_range:

                    lg.log_divider()

                    log.info(f'___Single target month: {target_month}___')

                    single_tot_day: int = 0
                    single_booked_day: int = 0
                    single_tot_day, single_booked_day = book_rate_cnt(driver, wait_time, target_month)
                    
                    all_tot_day += single_tot_day
                    all_booked_day += single_booked_day

                # --------------------------------

                book_rate = book_rate_cal(all_booked_day, all_tot_day)

            # --------------------------------

            inloop_key: str = f'{key}_booked_rate'
            for main_key in book_rate_data.keys():
                # log.info(f'inloop_key: {inloop_key} | main_key: {main_key} | book_rate: {book_rate}')
                if inloop_key == main_key:
                    book_rate_data[main_key] = book_rate
                    break

            lg.log_divider()

        utl.print_pretty_dict(book_rate_data)
        return book_rate_data

    except Exception as e:
        lg.log_detail_error(e)
        return book_rate_data 



def book_rate_cal(booked_day: int, tot_day: int) -> float | None:

    """
    operation: calculate book rate
    input:
        - booked_day: num of booked days in a month
        - tot_day: num of total days in a month
    output:
        - book rate: float | None
    """
    book_rate: float | None = None

    try:
        book_rate = float(booked_day / tot_day * 100)
        log.info(f'Total booked-rate: {booked_day} / {tot_day} = {book_rate:.2f}%')
    except ZeroDivisionError:
        book_rate = None
        log.info('No data to calculate book_rate')

    return book_rate



def book_rate_cnt(driver: WebDriver, wait_time: float, target_month: int) -> Tuple[int, int]:

    """
    operation: loop through each month
        1. count num of total days and booked days in each month
        2. find princing
            - if a month has > 3 days left
            - find checkout date
            - pick prev and checkout date
            - find price
    output:
        - num of total days in a month
        - num of booked days in a month
    """
    try:

        max_try: int = 12
        current_try: int = 0

        # --------------------------------

        while current_try < max_try:
            
            current_try += 1
            log.info(f'Try #{current_try}')

            # --------------------------------

            calender_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.c1e8f4ze')
            next_month_button: WebElement = calender_section.find_element(By.CSS_SELECTOR, 'div._qz9x4fc > button')
            month_sides: List[WebElement] = calender_section.find_elements(By.CSS_SELECTOR, 'div._1lds9wb') 
            
            month_pair: List[int] = []

            # --------------------------------

            for month_box in month_sides:
                month_name: WebElement = month_box.find_element(By.CSS_SELECTOR, 'h3')
                clean_month_name: int = cast(int, utl.get_info_from_string(month_name.text, mode='month'))
                month_pair.append(clean_month_name)

            # --------------------------------

            log.info(f'Target month: {target_month}')
            log.info(f'Current month_pair: {month_pair}')

            # --------------------------------

            if target_month in month_pair:
                log.info('At the right calendar view')
                time.sleep(wait_time)

                matched_month_box: WebElement = month_sides[0] if target_month == month_pair[0] else month_sides[1]
                date_list: List[WebElement] = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[class]')
                booked_day_list: List[WebElement] = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="true"]')

                tot_day: int = len(date_list)
                booked_day: int = len(booked_day_list)
                
                return tot_day, booked_day
            
            else:
                next_month_button.click()
                log.info('Wrong calendar view -> next_month_button clicked')
                time.sleep(wait_time)
        
        raise Exception('No visible calender data -> stop scraping target_month data')

    except Exception as e:
        lg.log_detail_error(e)
        return 0, 0




def price_info(driver: WebDriver, wait_time: float) -> int | None:

    lg.log_divider('Price info')

    price_data: int | None = None

    try:

        calender_section = driver.find_element(By.CSS_SELECTOR, 'div.c1e8f4ze')
        utl.scroll_focus_element(driver, calender_section)
        log.info('Calender section found')
        time.sleep(wait_time)
        
        # --------------------------------

        max_try: int = 12
        current_try: int = 0

        # --------------------------------

        while current_try < max_try:
            
            current_try += 1
            log.info(f'Try #{current_try}')

            # --------------------------------

            calender_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.c1e8f4ze')
            next_month_button: WebElement = calender_section.find_element(By.CSS_SELECTOR, 'div._qz9x4fc > button')
            month_sides: List[WebElement] = calender_section.find_elements(By.CSS_SELECTOR, 'div._1lds9wb') 

            # --------------------------------

            for month_box in month_sides:
                month_name: WebElement = month_box.find_element(By.CSS_SELECTOR, 'h3')
                clean_month_name: int = cast(int, utl.get_info_from_string(month_name.text, mode='month'))

                log.info(f'_____Current month: {clean_month_name}_____')
                
                # --------------------------------

                defualt_avai_day_list: List[WebElement] = month_box.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="false"]')

                if len(defualt_avai_day_list) == 0:
                    log.error(f'No available days to check pricing -> check next month_box')
                    continue

                # --------------------------------

                for idx in range(2):

                    log.info(f'--- Click iteration {idx + 1}/2 ---')
                        
                    try:
                        current_avai_day_list: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="false"]')
                        
                        avai_day: WebElement = current_avai_day_list[0]
                        avai_day_text: str = avai_day.text
                        avai_day.click()
                        log.info(f'Click {idx + 1}/2 -> choose day #{avai_day_text}')
                        time.sleep(wait_time)

                    except Exception as e:
                        log.error(f'Error scraping pricing at click iteration {idx + 1}')
                        return

                # --------------------------------

                price_css_list: List[Dict[str, str]] = [
                    {'type': 'Normal', 'css': 'span.umg93v9'},
                    {'type': 'Discounted', 'css': 'span.umuerxh'},
                ]
                
                for config in price_css_list:
                    price_element: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, config['css'])
                    if price_element:
                        log.info(f'{config["type"]} price element found')

                        price = cast(int, utl.get_info_from_string(price_element[1].text, mode='price'))
                        log.info(f'{config["type"]} price: {price:.0f} VND')

                        price_data = price
                        return price_data

                log.info('No price element found -> check next month_box')

                # --------------------------------
                
            for idx in range(2):
                next_month_button.click()
                time.sleep(wait_time)

            log.info('Both months has no available days to check pricing -> next_month_button clicked twice')

            # --------------------------------

        log.info('No available days in 1 year from now -> return None')
        return price_data

    except Exception as e:
        lg.log_detail_error(e)
        return price_data

