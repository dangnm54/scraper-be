import logging
import re
import time
from typing import Dict, Any, List, cast

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import src.tool.log_op as lg
import src.tool.utils as utl
import src.tool.api_op as api_op


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def get_book_rate(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    - input: response (json) of 3 months
    - operation:extract book rate info from given response (json)
    """

    lg.log_divider('Get book rate')

    book_rate_data: Dict[str, Any] = {
        'this_month_booked_rate': None,  # Optional[float]
        'next_1_month_booked_rate': None,  # Optional[float]
        'next_3_month_booked_rate': None,  # Optional[float]
    }

    # ------------------------

    try:

        month_list: List[Dict[str, Any]] = response.get('calendarMonths',[])

        cum_day: int = 0
        cum_booked: int = 0
        
        for idx, month in enumerate[Dict[str, Any]](month_list):
            
            month_name: str = month.get('month', '')
            log.info(f'Index #{idx}: month {month_name}')

            # ------------------------

            day_list: List[Dict[str, Any]] = month.get('days',[])
            
            day_cnt: int = len(day_list)
            # log.info(f'Total day count: {day_cnt}')
            
            booked_cnt: int = sum(1 for day in day_list if 
                day.get('available', False) == False and 
                day.get('availableForCheckout', False) == False
            )
            # log.info(f'Booked day count: {booked_day_cnt}')

            # ------------------------

            cum_day += day_cnt
            cum_booked += booked_cnt

            # ------------------------

            match idx:
                case 0:
                    book_rate_data['this_month_booked_rate'] = book_rate_cal(booked_cnt, day_cnt)
                case 1:
                    book_rate_data['next_1_month_booked_rate'] = book_rate_cal(booked_cnt, day_cnt)
                case 2:
                    book_rate_data['next_3_month_booked_rate'] = book_rate_cal(cum_booked, cum_day)

        # ------------------------

        utl.print_pretty_dict(book_rate_data)
        return book_rate_data

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_book_rate')
        return book_rate_data



def book_rate_cal(booked_day_cnt: int, day_cnt: int) -> float | None:
    book_rate: float | None = None
    try:
        book_rate = float(booked_day_cnt / day_cnt * 100)
        log.info(f'Total booked-rate: {booked_day_cnt} / {day_cnt} = {book_rate:.2f}%')
    except ZeroDivisionError:
        book_rate = None
        log.info('No data to calculate book_rate')
    except Exception as e:
        lg.log_detail_error(e, 'Error in book_rate_cal')
        return None

    return book_rate



def get_price(response: Dict[str, Any]) -> int | None:

    lg.log_divider('Get price')

    price_data: int | None = None

    # ------------------------

    try:    
        price_resp: Dict[str, Any] = api_op.get_response_part(response, 'price')
        price_str: str = price_resp.get('explanationData',{}).get('priceDetails',[])[0].get('items',[])[0].get('description','')

        price_data = cast(int, utl.get_info_from_string(price_str, 'price'))
        log.info(f'Price data: {price_data}')
        
        return price_data

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_price')
        return price_data



def get_overview_info(response: Dict[str, Any]) -> Dict[str, Any]:

    lg.log_divider('Get overview info')

    overview_data: Dict[str, Any] = {
        'guest_num': None,  # Optional[int]
        'bed_num': None,  # Optional[int]
        'bath_num': None,  # Optional[int]
        'location': None,  # Optional[str]
        'ggmap_link': None,  # Optional[str]
    }

    # ------------------------

    try:
        overview_resp: Dict[str, Any] = api_op.get_response_part(response, 'overview')
        info_list: List[Dict[str, Any]] = overview_resp.get('overviewItems',[])

        # ------------------------
        
        for item in info_list:
            for key, value in item.items():
                if key == 'title':
                    value1: str = utl.clean_text_2(value, mode='strip_"')
                    value2: str = utl.clean_text_2(value1, mode='normalize')
                    num: int = cast(int, utl.get_info_from_string(value2, mode='int'))

                    if num:
                        if 'khach' in value2:
                            overview_data['guest_num'] = num
                        if 'giuong' in value2:
                            overview_data['bed_num'] = num
                        if 'tam' in value2:
                            overview_data['bath_num'] = num

        # ------------------------

        location_resp: Dict[str, Any] = api_op.get_response_part(response, 'location')

        # ------------------------

        lat: str = location_resp.get('lat', '')
        lng: str = location_resp.get('lng', '')
        location = f'{lat},{lng}'
        overview_data['location'] = location

        # ------------------------

        ggmap_link: str = cast(str, utl.get_info_from_string(location, mode='ggmap_link'))
        overview_data['ggmap_link'] = ggmap_link

        # ------------------------

        utl.print_pretty_dict(overview_data)
        return overview_data

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_overview_info')
        return overview_data





def get_host_info(response: Dict[str, Any]) -> Dict[str, Any]:

    lg.log_divider('Get host info')

    host_data: Dict[str, Any] = {
        'host_name': None,  # Optional[str]
        'host_title': None,  # Optional[str]
        'host_rating_star': None,  # Optional[float]
        'host_rating_num': None,  # Optional[int]
        'host_exp': None,  # Optional[str]
        'host_link': None,  # Optional[str]
    }

    # ------------------------

    try:
        utl.print_pretty_dict(response)
        # host_overview_resp: Dict[str, Any] = api_op.get_response_part(response, 'host')


        return host_data
        
    except Exception as e:
        lg.log_detail_error(e, 'Error in get_host_info')
        return host_data











def click_calender(driver: WebDriver, wait_time: float):

    lg.log_divider('click_calender')

    try:

        calender_section = driver.find_element(By.CSS_SELECTOR, 'div.c1e8f4ze')
        utl.scroll_focus_element(driver, calender_section)
        log.info('Calender section found')
        time.sleep(wait_time)
        
        # --------------------------------

        max_try: int = 6
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
                    log.error(f'No available days to select check-in & check-out dates -> check next month_box')
                    continue

                # --------------------------------

                for idx in range(2):
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
                
                return

                # --------------------------------
                
            for idx in range(2):
                next_month_button.click()
                time.sleep(wait_time)

            # --------------------------------

        log.info('No available days in 6 months from now -> return None')
        return

    except Exception as e:
        lg.log_detail_error(e, 'Error in click_calender')
        return



def get_host_id(driver: WebDriver) -> int | None:

    lg.log_divider('get_host_id')

    host_id: int | None = None

    try:
        id_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.c1416qhh > a')
        log.info(f'Found host info card')
        
        url: str | None = id_element.get_attribute('href')
        log.info(f'Host URL: {url}')

        # ------------------------

        if url:
            match = re.search(r'/profile/(\d+)', url)
            if match:
                host_id = int(match.group(1))
            else:
                log.error('No id found in host URL')
                return None
        else:
            log.error('No host URL found')
            return None

        # ------------------------

        log.info(f'Host ID: {host_id}')
        return host_id

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_host_id')
        return None
