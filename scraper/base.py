import sys
import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Literal
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions


sys.path.append(os.path.dirname(os.path.dirname(__file__)))


# When running from root directory (FastAPI)
import scraper.tool.file_op as fop
import scraper.detail_step.browser as brws
import scraper.detail_step.scrape_p1 as scr1
import scraper.detail_step.scrape_p2 as scr2
import scraper.detail_step.calculation as cal
import scraper.detail_step.dashboard as dshb
import scraper.tool.log_op as lg
import scraper.tool.utils as utl
import scraper.tool.db_op as dbop

from scraper.tool.config import proxy_user, proxy_password, proxy_ip, proxy_port
from scraper.tool.config import driver_path, wait_time
from scraper.tool.config import main_website_url, ip_website_url

from scraper.type.data import PropertyDetail, ScrapeResult, PropertyDB
from sqlalchemy.orm import Session
from uuid import UUID, uuid4



# -----------------------------------------------------------------------------------


if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()


log = logging.getLogger(__name__)





def start_driver() -> Tuple[WebDriver | None, WebDriverWait | None]:

    extension_dir: str = brws.crt_proxy_helper_extention(proxy_user, proxy_password, proxy_ip, proxy_port)
    options_1: EdgeOptions = brws.config_basic_driver_setting()
    options_2: EdgeOptions | None = brws.config_advanced_driver_setting(extension_dir, options_1)
    

    if options_2 != None:
        driver: WebDriver | None = None
        wait: WebDriverWait | None = None
        driver, wait = brws.start_browser(driver_path, options_2)


    if driver != None and wait != None:
        # scr1.go_to_website(driver, wait, wait_time, ip_website_url)
        # brws.close_browser(driver)
        pass
    else:
        log.error(f"Cannot create driver and wait")

    return driver, wait





def scrape_p1(db: Session,main_website_url, 
            file_name: str, location: str, num_guest: int, num_property: int,
    ) -> List[PropertyDB]:
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"An error in 'if driver'")
        return []


    scr1.go_to_website(driver, wait, wait_time, main_website_url, view='main_page')
    scr1.search_location(driver, wait_time, location)
    scr1.search_date(driver, wait_time)
    scr1.search_guest(driver, wait_time, num_guest)
    scr1.press_search(driver)

    link_list: List[Dict[str, str]] = scr1.view_page_get_all_link(driver, wait, wait_time, num_property)

    brws.close_browser(driver)
    
    if not link_list:
        log.error(f"link_list is empty: {link_list}")
        link_csv_path = []

    
    link_list_db: List[PropertyDB] = []
    for prop in link_list:
        prop_row = (PropertyDB(
            prop_code=prop['prop_code'],
            prop_name=prop['prop_name'],
            prop_link=prop['prop_link']
        ))
        db.add(prop_row)
        link_list_db.append(prop_row)

    
    db.commit()
    log.info(f'Saved {len(link_list_db)} properties (basic info) to database')


    # update prop object in Python with data created by db after during the commit (like timestamp)
    for prop in link_list_db:
        db.refresh(prop)


    return link_list_db


    link_df = fop.list_dict_to_df(link_list, index='prop_code')
    link_csv_path = fop.df_to_csv(link_df, name=f'{file_name}_link')
    


    

    return link_csv_path





def scrape_p2(property_link_csv_path: str,
            file_name: str, collect_host_data: bool=False, collect_booking_rate: bool=False,
    ) -> List[PropertyDetail]:

    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"An error in 'if driver'")
        return []


    link_df: pd.DataFrame = fop.csv_to_df(property_link_csv_path, index='prop_code', mode=1)
    detail_list: List[PropertyDetail] = []

    cnt = 1


    for index, row in link_df.iterrows():
        # print(f'{index} | {row["name"]} | {row["link"]}')

        if cnt < 3:
            cnt += 1
            continue

        property_detail_data: Dict[str, Any] = {
            # overview_data
            'prop_code': index,  # str
            'prop_name': row['prop_name'],  # str
            'prop_link': row['prop_link'],  # str

            'scrape_result': None,  # ScrapeResult
            'guest_num': None,  # Optional[int]
            'bed_num': None,  # Optional[int]
            'bath_num': None,  # Optional[int]
            'location': None,  # Optional[str]
            
            # rating_data
            'rating_title': None,  # Optional[str]
            'rating_star': None,  # Optional[float]
            'rating_num': None,  # Optional[int]
            
            # host_data
            'host_name': None,  # Optional[str]
            'host_title': None,  # Optional[str]
            'host_rating_star': None,  # Optional[float]
            'host_rating_num': None,  # Optional[int]
            'host_exp': None,  # Optional[str]
            'host_link': None,  # Optional[str]
            
            # booking_rate_data
            'this_month_booked_rate': None,  # Optional[float]
            'next_1_month_booked_rate': None,  # Optional[float]
            'next_3_month_booked_rate': None,  # Optional[float]
        } 

        log.info(f'Scraping property: {index} - {row["prop_name"]}')
        
        scr1.go_to_website(driver, wait, wait_time, row['prop_link'], view='detail_page')

        try:
            overview_data: Dict[str, Any] = scr2.overview_info(driver, wait)
            property_detail_data.update(overview_data)
    
            rating_data: Dict[str, Any] = scr2.rating_info(driver)
            property_detail_data.update(rating_data)

            if collect_host_data:
                host_data: Dict[str, Any] = scr2.host_info(driver)
                property_detail_data.update(host_data)

            if collect_booking_rate:
                book_rate_data: Dict[str, Any] = scr2.book_rate_info(driver, wait_time)
                property_detail_data.update(book_rate_data)

        except Exception as e:
            lg.log_detail_error(e)


        scrape_result: ScrapeResult = scr2.get_scrape_result(property_detail_data)
        property_detail_data['scrape_result'] = scrape_result

        lg.log_divider()

        utl.print_pretty_dict(property_detail_data) 
        detail_instance: PropertyDetail = PropertyDetail(**property_detail_data)
        detail_list.append(detail_instance)

        log.info(f"Finish scraping {len(detail_list)} properties")

        lg.log_divider()

    brws.close_browser(driver)  

    return detail_list



def calculate_data(csv_path):

    full_df = fop.csv_to_df(csv_path, index='prop_code', mode=2)

    cnt_rating_cate_df = cal.cnt_rating_categories(full_df)

    return cnt_rating_cate_df





def draw_dashboard(csv_path, cal_data):
    
    full_df = fop.csv_to_df(csv_path, index='prop_code', mode=2)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes_list = axes.flatten()

    dshb.util_num_rating_star(axes_list[0], full_df)
    dshb.rating_category_ratio(axes_list[1], cal_data)
    dshb.rating_num_rating_star(axes_list[2], full_df)
    dshb.this_month_BR_rating_star(axes_list[3], full_df)
    dshb.next_1month_BR_rating_star(axes_list[4], full_df)
    dshb.next_3month_BR_rating_star(axes_list[5], full_df)

    plt.tight_layout()
    plt.show()



# -----------------------------------------------------------------------------------



def run_full_flow(
        db: Session,
        file_name: str,
        location: str,
        num_guest: int,
        num_property: int,
        collect_host_data: bool = False,
        collect_booking_rate: bool = False,
        mode: Literal['csv', 'db'] = 'csv'
    ) -> Dict[str, str]:

    lg.log_divider('Start full flow')

    log.info("API Request Received:")
    log.info(f"""    
    - Location: {location}
    - Number of guests: {num_guest}
    - Number of properties: {num_property}
    - Collect host data: {collect_host_data}
    - Collect booking rate: {collect_booking_rate}
    """)

    session_id: UUID = uuid4()
    log.info(f"New scraping session started with ID: {session_id}")

    # session_name:


    link_list_db: List[PropertyDB] = scrape_p1(db, main_website_url, file_name, location, num_guest, num_property)
    # log.info(f"Phase 1 (link scraping) completed. File saved to: {link_csv_path}")
    # link_csv_path: str = r'C:\Users\ADMIN\Pictures\scraper\scraper-be\data\PhoCo_link_130825.csv'

    detail_property_list: List[PropertyDetail] = scrape_p2(link_csv_path, file_name, collect_host_data, collect_booking_rate)

    log.info(f'Start saving data | destination: {mode}')

    try:
        if mode == 'db':
            dbop.save_data_to_db(detail_property_list, db, session_id, file_name)

        elif mode == 'csv':
            detail_dict_list: List[Dict[str, Any]] = [property.model_dump() for property in detail_property_list]
            full_df: pd.DataFrame = fop.list_dict_to_df(detail_dict_list, index='prop_code') 
            full_csv_path: str = fop.df_to_csv(full_df, name=f'{file_name}_full')
            log.info(f"Phase 2 (detail scraping) completed. File saved to: {full_csv_path}")
        
        log.info(f"detail: Complete saving data")
    
    except Exception as e:
        log.error(f"detail: Error in saving data: {e}")
        

    return {f"detail": "Complete scraping process"}



# -----------------------------------------------------------------------------------


if __name__ == "__main__":
    db_session: Session | None = dbop.create_db_session()

    if db_session:
        try: 
            run_full_flow(
                db = db_session,
                file_name = 'PhoCo',
                location = 'Pho Co, hanoi',
                num_guest = 2,
                num_property = 3,
                collect_host_data = True,
                collect_booking_rate = True
            )
        finally:
            log.info("Closing database session for direct file run.")
            db_session.close()

    else:  
        log.error("Could not create database session.")



# start_driver()

print(f'\nLog file saved to: {log_file_path}\n')