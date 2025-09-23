# load .env file for local use
from dotenv import load_dotenv
load_dotenv()

import sys
import os
import logging
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from typing import Any, Dict, List, Tuple, Literal

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# When running from root directory (FastAPI)
import src.detail_step.browser as brws
import src.detail_step.scrape_p1 as scr1
import src.detail_step.scrape_p2 as scr2
import src.tool.log_op as lg
import src.tool.db_op as dbop
import src.tool.utils as utl
from src.tool.config import wait_time


from src.tool.config import main_website_url, ip_website_url, search_mode, browser_mode, save_db

from src.type.data import ScrapeResult, ScrapeStatus, PropertyDB


# -----------------------------------------------------------------------------------


if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()


log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------


# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')

PROXY_USER: str | None = os.getenv('PROXY_USER')
PROXY_PASSWORD: str | None = os.getenv('PROXY_PASSWORD')
PROXY_IP: str | None = os.getenv('PROXY_IP')
PROXY_PORT: str | None = os.getenv('PROXY_PORT')

DRIVER_PATH: str | None = os.getenv('DRIVER_PATH')
LOG_FILE_PATH: str | None = os.getenv('LOG_FILE_PATH')


# -----------------------------------------------------------------------------------


def start_driver() -> Tuple[WebDriver | None, WebDriverWait | None]:

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

    if driver != None and wait != None:
        # scr1.go_to_website(driver, wait, wait_time, ip_website_url)
        # brws.close_browser(driver)
        pass
    else:
        log.error(f"Cannot create driver and wait")

    return driver, wait





def scrape_p1(db: Session, session_id: UUID, session_name: str, main_website_url: str, 
            location: str, num_guest: int, num_property: int,
            save_db: bool = False
    ) -> List[PropertyDB]:
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"Failed to start driver and create wait object")
        return []

    scr1.go_to_website(driver, wait, wait_time, main_website_url, view='main_page')

    log.info(f'Search mode: {search_mode}')

    match search_mode:
        case 'none':
            pass
        case 'apply':
            scr1.search_location(driver, wait_time, location)
            scr1.search_date(driver, wait_time)
            scr1.search_guest(driver, wait_time, num_guest)
            scr1.press_search(driver)

    link_list: List[Dict[str, str]] = scr1.view_page_get_all_link(driver, wait, wait_time, num_property, search_mode)

    brws.close_browser(driver)
    
    if not link_list:
        log.error(f"link_list is empty: {link_list}")
        return []
    
    link_list_db: List[PropertyDB] = []
    for property in link_list:
        prop: PropertyDB = (PropertyDB(
            session_id = session_id,
            session_name = session_name,
            prop_code = property['prop_code'],
            prop_name = property['prop_name'],
            prop_link = property['prop_link']
        ))
        
        if save_db:
            db.add(prop) # add object to session -> session track and know which python object is linked to which db object until session closed
            db.commit()
            log.info(f'Saved property <{prop.prop_code}> (basic info) to database')
        
        link_list_db.append(prop)

    log.info(f'Finish saving {len(link_list_db)} properties (basic info) to database')

    if save_db:
        # update prop object in Python with data created by db after during the commit (like timestamp)
        for prop in link_list_db:
            db.refresh(prop)

    return link_list_db





def scrape_p2(db: Session, detail_list_db: List[PropertyDB],
            collect_host_data: bool=False, collect_booking_rate: bool=False,
            save_db: bool = False
    ) -> ScrapeStatus:

    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    if driver and wait:
        pass
    else:
        log.error(f"Failed to start driver and create wait object")
        return ScrapeStatus.partial

    scraped_prop_cnt: int = 0
    saved_prop_cnt: int = 0

    for prop in detail_list_db:

        lg.log_divider()
        log.info(f'Scraping property: {prop.prop_code} - {prop.prop_name}')
        property_link: str = str(prop.prop_link)

        try:
            scr1.go_to_website(driver, wait, wait_time, property_link, view='detail_page')
        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to access page of property <{prop.prop_code}> -> skip to next property')
            continue


        try:
            overview_data: Dict[str, Any] = scr2.overview_info(driver, wait)
            rating_data: Dict[str, Any] = scr2.rating_info(driver)

            prop.guest_num = overview_data['guest_num']
            prop.bed_num = overview_data['bed_num']
            prop.bath_num = overview_data['bath_num']
            prop.location = overview_data['location']
            prop.ggmap_link = overview_data['ggmap_link']
            
            prop.rating_title = rating_data['rating_title']
            prop.rating_star = rating_data['rating_star']
            prop.rating_num = rating_data['rating_num']

            if collect_host_data:
                host_data: Dict[str, Any] = scr2.host_info(driver)

                prop.host_name = host_data['host_name']
                prop.host_title = host_data['host_title']
                prop.host_rating_star = host_data['host_rating_star']
                prop.host_rating_num = host_data['host_rating_num']
                prop.host_exp = host_data['host_exp']
                prop.host_link = host_data['host_link']

            if collect_booking_rate:
                book_rate_data: Dict[str, Any] = scr2.book_rate_info(driver, wait_time)

                prop.this_month_booked_rate = book_rate_data['this_month_booked_rate']
                prop.next_1_month_booked_rate = book_rate_data['next_1_month_booked_rate']
                prop.next_3_month_booked_rate = book_rate_data['next_3_month_booked_rate']
            

            scrape_result: ScrapeResult = scr2.get_scrape_result(prop)
            setattr(prop, 'scrape_result', str(scrape_result)) 
            log.info(f'Complete scraping data for property #{prop.prop_code} | result: {scrape_result}')
            scraped_prop_cnt += 1

        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to scrape all data of property <{prop.prop_code}> -> save already-scraped data to database')


        if save_db:
            try:
                db.commit()
                log.info(f'Saved property <{prop.prop_code}> (detail info) to database')
                saved_prop_cnt += 1
            except Exception as e:
                lg.log_detail_error(e)
                log.error(f'Error to save property <{prop.prop_code}> (detail info) to database')
                # clean up failed transaction (eg: failed commit)
                db.rollback()

        lg.log_divider()
        utl.print_pretty_dict(prop)


    log.info(f"Scraping process completed | {scraped_prop_cnt} properties scraped")
    log.info(f'Finish saving {saved_prop_cnt} properties (detail info) to database')
    
    brws.close_browser(driver)
    lg.log_divider()

    return ScrapeStatus.success





# -----------------------------------------------------------------------------------



def run_full_flow(
        db: Session,
        file_name: str, location: str, num_guest: int, num_property: int,
        collect_host_data: bool = False,
        collect_booking_rate: bool = False
    ) -> ScrapeStatus:

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
    session_name: str = dbop.get_session_name(db, file_name)
    log.info(f"New scraping session <{session_name}> started | ID: {session_id}")

    link_list_db: List[PropertyDB] = scrape_p1(db, session_id, session_name, main_website_url, location, num_guest, num_property, save_db)
    log.info(f"Phase 1 (link scraping) completed.")

    if not link_list_db:
        log.error(f"Phase 1 didn't find any properties -> Stop scraping process")
        return ScrapeStatus.failed

    scrape_status: ScrapeStatus = scrape_p2(db, link_list_db, collect_host_data, collect_booking_rate, save_db)
    log.info(f"Phase 2 (detail scraping) completed.")
    
    return scrape_status



# -----------------------------------------------------------------------------------


if __name__ == "__main__":
    db_session: Session | None = dbop.create_db_session()


    log.info("""Config:
    - save_db: {save_db}
    - search_mode: {search_mode}
    - browser_mode: {browser_mode}
    - log_error_level: {log_error_level}
    """)

    if db_session:
        try: 
            run_full_flow(
                db = db_session,
                file_name = 'PhoCo',
                location = 'Pho Co, hanoi',
                num_guest = 2,
                num_property = 1,
                # collect_host_data = True,
                # collect_booking_rate = True
            )
        finally:
            log.info("Closing database session for direct file run.")
            db_session.close()

    else:  
        log.error("Could not create database session.")



# start_driver()

print(f'\nLog file saved to: {LOG_FILE_PATH}\n')






# log info của mấy config kh đc

# lỗi ở view_page_get_all_link (có ads ở trang này)

"""

============================== View page and get all link

09:56:08 | INFO | scrape_p1 - view_page_get_all_link - 233 | Ready to scrape 1 properties | Search-mode: apply
09:56:28 | ERROR | log_op - log_detail_error - 146 | Message: 

- Error level #1: File <scrape_p1.py> | Function <view_page_get_all_link> | Line #240: wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,'div.cy5jw6o')))
- Error level #2: File <wait.py> | Function <until> | Line #138: raise TimeoutException(message, screen, stacktrace)


============================== Close browser

09:56:31 | INFO | browser - close_browser - 220 | Close browser
09:56:31 | ERROR | base - scrape_p1 - 129 | link_list is empty: []
09:56:31 | INFO | base - run_full_flow - 290 | Phase 1 (link scraping) completed.
09:56:31 | ERROR | base - run_full_flow - 293 | Phase 1 didn't find any properties -> Stop scraping process
09:56:31 | INFO | base - <module> - 329 | Closing database session for direct file run.

"""