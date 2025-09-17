import time
import logging
from typing import Dict, Any, List, Tuple, cast

from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

try:
    import app.tool.utils as utl
    import app.tool.log_op as lg
    from app.type.data import ScrapeResult, PropertyDB
    import app.tool.get_ipt as ipt
except ImportError:
    import tool.utils as utl
    import tool.log_op as lg
    from type.data import ScrapeResult, PropertyDB
    import tool.get_ipt as ipt


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def overview_info(driver: WebDriver, wait: WebDriverWait) -> Dict[str, Any]:

    lg.log_divider('Overview info')
    
    overview_data: Dict[str, Any] = {
        'guest_num': None,  # Optional[int]
        'bed_num': None,  # Optional[int]
        'bath_num': None,  # Optional[int]
        'location': None,  # Optional[str]
        'ggmap_link': None,  # Optional[str]
    }

    try:
    
        overview_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="OVERVIEW_DEFAULT_V2"]')
        log.info('Overview section found')

        info_list: List[WebElement] = overview_section.find_elements(By.CSS_SELECTOR, 'li.l7n4lsf')
        for info in info_list:
            clean_info1: str = utl.clean_text(info.text, mode=2)
            clean_info2: str = utl.clean_text(clean_info1, mode=1)

            num: int = cast(int, utl.get_info_from_string(clean_info2, mode='int'))

            if num:
                if 'khach' in clean_info2:
                    overview_data['guest_num'] = num
                if 'giuong' in clean_info2:
                    overview_data['bed_num'] = num
                if 'tam' in clean_info2:
                    overview_data['bath_num'] = num

        location_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="LOCATION_DEFAULT"]')
        utl.scroll_focus_element(driver, location_section)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[title="Báo cáo lỗi trong bản đồ đường hoặc hình ảnh đến Google"]')))
        location_element: WebElement = location_section.find_element(By.CSS_SELECTOR, 'a[title="Báo cáo lỗi trong bản đồ đường hoặc hình ảnh đến Google"]')
        location: str | None = location_element.get_attribute('href')
        
        if location:
            clean_location: str = cast(str, utl.get_info_from_string(location, mode='coordinate'))
            overview_data['location'] = clean_location

            ggmap_link: str = cast(str, utl.get_info_from_string(clean_location, mode='ggmap_link'))
            overview_data['ggmap_link'] = ggmap_link
        
        utl.print_pretty_dict(overview_data)
        return overview_data
    
    except Exception as e:
        lg.log_detail_error(e)
        return overview_data



# def utility_info(driver, wait_time):

    lg.log_divider('Utility info')

    try:
        utility_data = {
            # 'Utility_num': None,
            # 'Utility_bathroom': None,
            # 'Utility_bedroom': None,
            # 'Utility_entertain': None,
            # 'Utility_safety': None,
            # 'Utility_kitchen': None,
            # 'Utility_outdoor': None,
            # 'Utility_parking': None,
            # 'Utility_service': None,
            # 'Utility_not_included': None,
        }

        utility_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="AMENITIES_DEFAULT"]')
        utility_button = utility_section.find_element(By.CSS_SELECTOR, 'button.l1ovpqvx')
        utl.scroll_focus_element(driver, utility_button)

        # utility_num = utl.get_info_from_string(utility_button.text, mode='int')
        # utility_data['Utility_num'] = utility_num
        
        # utility_button.click()
        # time.sleep(wait_time)
        # log.info('Open utility modal')

        # utility_modal = driver.find_element(By.CSS_SELECTOR, 'div.d1pe7dt2')
        # utility_category_list = utility_modal.find_elements(By.CSS_SELECTOR,'div._11jhslp')

        # for category in tqdm(utility_category_list, desc='Scraping utility data: '):
        #     utl.scroll_focus_element(driver, category)

        #     item_list = []

        #     item_element_list = category.find_elements(By.CSS_SELECTOR, 'li')
        #     for item in item_element_list:
                
        #         non_striked_name = item.find_elements(By.CSS_SELECTOR, 'del')
        #         sub_name = item.find_elements(By.CSS_SELECTOR, 'div.s9gst5p')
        #         if non_striked_name:
        #             if sub_name:
        #                 item_name = f'{non_striked_name[0].text}\n{sub_name[0].text}'
        #             else:
        #                 item_name = non_striked_name[0].text
        #         else:
        #             item_name = item.text
        #         item_list.append(item_name)

        #     cate_name = category.find_element(By.CSS_SELECTOR, 'h2.hpipapi').text
        #     clean_cate_name = utl.clean_text(cate_name, mode=1)

        #     category_map = {
        #         'Utility_bathroom':'phong tam',
        #         'Utility_bedroom':'phong ngu',
        #         'Utility_entertain':'giai tri',
        #         'Utility_safety':'an toan',
        #         'Utility_kitchen':'bep',
        #         'Utility_outdoor':'ngoai troi',
        #         'Utility_parking':'do xe',
        #         'Utility_service':'dich vu',
        #         'Utility_not_included':'khong bao gom'
        #     }

        #     for key, cate_name in category_map.items():
        #         if cate_name in clean_cate_name:
        #             utility_data[key] = item_list

        #     log.info(f'\nCategory: {clean_cate_name}')
        #     log.info(f'Item list: {item_list}')
        #     lg.log_divider()
            
        # close_button = utility_modal.find_element(By.CSS_SELECTOR, 'button[aria-label="Đóng"]')
        # close_button.click()
        # log.info('Close modal')

        utl.print_pretty_dict(utility_data)
        return utility_data

    except Exception as e:
        lg.log_detail_error(e)
        return utility_data



def rating_info(driver: WebDriver) -> Dict[str, Any]:

    lg.log_divider('Rating info')

    rating_data: Dict[str, Any] = {
        'rating_title': None,  # Optional[str]
        'rating_star': None,  # Optional[float]
        'rating_num': None,  # Optional[int]
    }

    try:

        # overview data
        overview_rating_special_section: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, 'div.l57as01')
        if not overview_rating_special_section:
            overview_rating_special_section = driver.find_elements(By.CSS_SELECTOR, 'div.mreautf')
        overview_rating_normal_section: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, 'div.rgr5sph')

        if overview_rating_special_section:
            overview_rating_special: WebElement = overview_rating_special_section[0]
            utl.scroll_focus_element(driver, overview_rating_special)            
            log.info('Special rating element found')
            
            rating_title: WebElement = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.lbjrbi0')
            clean_rating_title: str = rating_title.text.replace('\n',' ')
            rating_data['rating_title'] = clean_rating_title

            rating_star_section: WebElement = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.a8jhwcl')
            rating_star_elements: List[WebElement] = rating_star_section.find_elements(By.CSS_SELECTOR, 'div')
            rating_star: str = utl.clean_text(rating_star_elements[0].text, mode=3)
            rating_data['rating_star'] = float(rating_star)

            rating_num_section: WebElement = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.r16onr0j')
            rating_num_elements: List[WebElement] = rating_num_section.find_elements(By.CSS_SELECTOR, 'div')
            special_rating_num: int = int(rating_num_elements[0].text)
            rating_data['rating_num'] = special_rating_num

            log.info('Special overview rating data collected')
            
        elif overview_rating_normal_section:
            overview_rating_normal: WebElement = overview_rating_normal_section[0]
            utl.scroll_focus_element(driver, overview_rating_normal)            
            log.info('Normal rating element found')

            rating_star_element: WebElement = overview_rating_normal.find_element(By.CSS_SELECTOR, 'div.rmtgcc3')
            rating_star: str = utl.clean_text(rating_star_element.text, mode=3)
            rating_data['rating_star'] = float(rating_star)

            rating_num_element: WebElement = overview_rating_normal.find_element(By.CSS_SELECTOR, 'a')
            normal_rating_num: int = cast(int, utl.get_info_from_string(rating_num_element.text, mode='int'))
            rating_data['rating_num'] = normal_rating_num
            
            log.info('Normal overview rating data collected') 


        # detail data
        # rating_detail_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="REVIEWS_DEFAULT"]')
        # log.info('Rating section found')

        # rating_category_list = rating_detail_section.find_elements(By.CSS_SELECTOR, 'div.l925rvg')
        # for category in tqdm(rating_category_list, desc='Scraping rating detail data: '):
        #     utl.scroll_focus_element(driver, category)

        #     detail_element = category.find_elements(By.CSS_SELECTOR, 'div')
        #     category_name = utl.clean_text(detail_element[0].text, mode=1)
        #     category_rating = utl.clean_text(detail_element[1].text, mode=3)

        #     rating_map = {
        #         'Rating_clean_score':'sach se',
        #         'Rating_accuracy_score':'chinh xac',
        #         'Rating_checkin_score':'nhan phong',
        #         'Rating_commu_score':'giao tiep',
        #         'Rating_location_score':'vi tri',
        #         'Rating_value_score':'gia tri',
        #     }

        #     for key, cate_name in rating_map.items():
        #         if cate_name in category_name:
        #             rating_data[key] = category_rating

        #     log.info(f'\nCategory: {category_name}')
        #     log.info(f'Rating: {category_rating}')
        #     lg.log_divider()


        utl.print_pretty_dict(rating_data)
        return rating_data

    except Exception as e:
        lg.log_detail_error(e)
        return rating_data    



def host_info(driver: WebDriver) -> Dict[str, Any]:

    lg.log_divider('Host info')

    host_data: Dict[str, Any] = {
        'host_name': None,  # Optional[str]
        'host_title': None,  # Optional[str]
        'host_rating_star': None,  # Optional[float]
        'host_rating_num': None,  # Optional[int]
        'host_exp': None,  # Optional[str]
        'host_link': None,  # Optional[str]
    }
    
    try:

        host_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.c1h2ee1b')
        utl.scroll_focus_element(driver, host_section)

        host_name: str = host_section.find_element(By.CSS_SELECTOR, 'span.t1gpcl1t').text
        host_data['host_name'] = host_name

        host_title_element: List[WebElement] = host_section.find_elements(By.CSS_SELECTOR, 'span.s1h3l0w7')
        host_title: str = host_title_element[0].text
        if host_title != 'Host':
            host_data['host_title'] = host_title


        host_detail_section: WebElement = host_section.find_element(By.CSS_SELECTOR, 'div.s13au5n7')


        host_rating_star: WebElement = host_detail_section.find_element(By.CSS_SELECTOR, 'div.rz5w5y3')
        clean_host_rating_star: str = utl.clean_text(host_rating_star.text, mode=3)
        host_data['host_rating_star'] = float(clean_host_rating_star)

        host_rating_num: WebElement = host_detail_section.find_element(By.CSS_SELECTOR, 'span[data-testid="Đánh giá-stat-heading"]')
        clean_host_rating_num1: str = utl.clean_text(host_rating_num.text, mode=4)
        clean_host_rating_num2: int = cast(int, utl.get_info_from_string(clean_host_rating_num1, mode='int'))
        host_data['host_rating_num'] = clean_host_rating_num2


        host_exp: List[WebElement] = host_detail_section.find_elements(By.CSS_SELECTOR, 'span.a8jt5op')
        if len(host_exp) == 3:
            host_exp_element: WebElement = host_exp[2]
            clean_host_exp: str = cast(str, utl.get_info_from_string(host_exp_element.text, mode='exp'))
            host_data['host_exp'] = clean_host_exp

        host_avatar: WebElement = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Xem Hồ sơ đầy đủ của Chủ nhà/Người tổ chức"]')
        host_link: str | None = host_avatar.get_attribute('href')
        if isinstance(host_link, str):
            host_data['host_link'] = host_link


        utl.print_pretty_dict(host_data)
        return host_data

    except Exception as e:
        lg.log_detail_error(e)
        return host_data



# def co_host_info(driver):

    lg.log_divider('Co-host info')

    try:
        co_host_data = {
            'Co_host_num': None,
            'Co_host_name': None,
            'Co_host_link': None,
        }

        co_host_section = driver.find_elements(By.CSS_SELECTOR, 'ul.ato18ul')
        if co_host_section:
            utl.scroll_focus_element(driver, co_host_section[0])
            co_host_num = int(len(co_host_section))
            co_host_data['Co_host_num'] = co_host_num
    
            co_host_list = co_host_section[0].find_elements(By.CSS_SELECTOR, 'li.ahxgcvj')
            name_list = []
            link_list = []

            for host in tqdm(co_host_list, desc='Scraping co-host data: '):
                name = host.find_element(By.CSS_SELECTOR, 'span.a7xbq6p').text
                name_list.append(name)

                link_element = host.find_element(By.CSS_SELECTOR, 'a._1991pnj5')
                link = link_element.get_attribute('href')
                link_list.append(link)

                log.info(f'Co-host name: {name}')
                log.info(f'Co-host link: {link}')

            co_host_data['Co_host_name'] = name_list
            co_host_data['Co_host_link'] = link_list

        else:
            co_host_data['Co_host_num'] = 0
            log.info('No co-host')

        utl.print_pretty_dict(co_host_data)
        return co_host_data

    except Exception as e:
        lg.log_detail_error(e)
        return co_host_data



def book_rate_info(driver: WebDriver, wait_time: float) -> Dict[str, Any]:

    lg.log_divider('Book rate info')

    book_rate_data: Dict[str, Any] = {
        'this_month_booked_rate': None,  # Optional[float]
        'next_1_month_booked_rate': None,  # Optional[float]
        'next_3_month_booked_rate': None,  # Optional[float]
    }

    month_data: Dict[str, Any] = ipt.get_date_for_book_data()

    try:

        book_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="BOOK_IT_SIDEBAR"]')
        utl.scroll_focus_element(driver, book_section)
        log.info('Book time section found')

        start_date_element: WebElement = book_section.find_element(By.CSS_SELECTOR, 'div._19y8o0j')
        start_date_element.click()

        log.info('Open calender')
        time.sleep(wait_time)
        lg.log_divider()

        # month_data struc
        # month_data: Dict[str, Any] = {
        #     'this_month': 0, # int
        #     'next_1_month': 0, # int
        #     'next_3_month': [], # List[int]
        # }        

        for key, month in month_data.items():

            book_rate: float | None = None

            if type(month) == int:
                # continue
                target_month: int = month
                log.info(f'_____Target month: {target_month}_____')

                tot_date: int = 0
                booked_date: int = 0
                tot_date, booked_date = detail_booking_cal(driver, wait_time, target_month)

                book_rate = final_stage_book_cal(booked_date, tot_date)


            elif type(month) == list:
                target_month_range: List[int] = month
                log.info(f'_____Target month_list: {target_month_range}_____')

                all_tot_date: int = 0
                all_booked_date: int = 0
                
                for target_month in target_month_range:

                    lg.log_divider()

                    log.info(f'___Single target month: {target_month}___')

                    single_tot_date: int = 0
                    single_booked_date: int = 0
                    single_tot_date, single_booked_date = detail_booking_cal(driver, wait_time, target_month)
                    
                    all_tot_date += single_tot_date
                    all_booked_date += single_booked_date

                book_rate = final_stage_book_cal(all_booked_date, all_tot_date)


            inloop_key: str = f'{key}_booked_rate'
            for key_otp in book_rate_data.keys():
                # log.info(f'inloop_key: {inloop_key} | key_otp: {key_otp} | book_rate: {book_rate}')
                if inloop_key == key_otp:
                    book_rate_data[key_otp] = book_rate
                    break

            lg.log_divider()

        utl.print_pretty_dict(book_rate_data)
        return book_rate_data

    except Exception as e:
        lg.log_detail_error(e)
        return book_rate_data 



def final_stage_book_cal(booked_date: int, tot_date: int) -> float | None:

    book_rate: float | None = None

    try:
        book_rate = float(booked_date / tot_date * 100)
        log.info(f'Total booked-rate: {booked_date} / {tot_date} = {book_rate:.2f}%')
    except ZeroDivisionError:
        book_rate = None
        log.info('No data to calculate book_rate')

    return book_rate



def detail_booking_cal(driver: WebDriver, wait_time: float, target_month: int) -> Tuple[int, int]:

    try:
        max_try: int = 12
        current_try: int = 0
        while current_try < max_try:
            current_try += 1
            log.info(f'Try #{current_try}')

            calender_section: WebElement = driver.find_elements(By.CSS_SELECTOR, 'div.c1e8f4ze')[1]
            button_section: WebElement = calender_section.find_element(By.CSS_SELECTOR, 'div._5neba7a')
            last_month_button: WebElement = button_section.find_element(By.CSS_SELECTOR, 'button[aria-label="Chuyển sang tháng trước."]')
            next_month_button: WebElement = button_section.find_element(By.CSS_SELECTOR, 'button[aria-label="Di chuyển lên trên để chuyển sang tháng sau."]')

            month_sides: List[WebElement] = calender_section.find_elements(By.CSS_SELECTOR, 'div._1lds9wb') 
            month_pair: List[int] = []

            for month_box in month_sides:
                month_name: WebElement = month_box.find_element(By.CSS_SELECTOR, 'h3')
                clean_month_name: int = cast(int, utl.get_info_from_string(month_name.text, mode='month'))
                month_pair.append(clean_month_name)
            
            log.info(f'Target month: {target_month}')
            log.info(f'Current month_pair: {month_pair}')

            if target_month in month_pair:
                log.info('At the right calendar view')
                time.sleep(wait_time)

                matched_month_box: WebElement = month_sides[0] if target_month == month_pair[0] else month_sides[1]
                date_list: List[WebElement] = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[class]')
                booked_date_list: List[WebElement] = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="true"]')

                tot_date: int = len(date_list)
                booked_date: int = len(booked_date_list)
                
                return tot_date, booked_date
            
            else:
                if target_month < month_pair[0]:

                    if last_month_button.is_enabled():
                        last_month_button.click()
                        log.info('Wrong calendar view -> last_month_button clicked')
                        time.sleep(wait_time)
                    else:
                        log.info('No visible calender data -> stop scraping target_month data')
                        lg.log_divider()
                        return 0, 0

                elif target_month > month_pair[1]:
                    next_month_button.click()
                    log.info('Wrong calendar view -> next_month_button clicked')
                    time.sleep(wait_time)
        
        raise Exception('No visible calender data -> stop scraping target_month data')

    except Exception as e:
        lg.log_detail_error(e)
        return 0, 0
    


def get_scrape_result(property_detail_data: PropertyDB) -> "ScrapeResult":

    lg.log_divider('Get scrape result')

    property_detail_dict: Dict[str, Any] = utl.obj_to_dict(property_detail_data)
    value_list: List[Any] = [v for k, v in property_detail_dict.items() if k != 'scrape_result']

    none_count: int = value_list.count(None)
    total_count: int = len(value_list)

    result: "ScrapeResult" = 'Failed'

    if all(value is None for value in value_list):
        result = 'Failed'
    elif not all(value is None for value in value_list) and None in value_list:
        result = 'Partial'
    else:
        result = 'Success'

    log.info(f'Missing data (exclude result field): {none_count} / {total_count} -> Scraping result: {result}')

    return result