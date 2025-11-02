import sys
import os
from type.data import PropertyDB
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


from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Tuple, Literal, cast, get_args

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions

# When running from root directory (FastAPI)
import src.detail_step.browser as brws
import src.detail_step.scrape1 as scr1
import src.detail_step.scrape2 as scr2
import src.detail_step.scrape3 as scr3
import src.tool.db_op as dbop
import src.tool.utils as utl
import src.detail_step.shared_state as shared_state

from src.tool.config import wait_time
from src.tool.config import main_website_url, ip_website_url, search_mode, save_db, log_error_level, scrape_phase, test_local
from src.type.data import ScrapeResult, ScrapeStatus, PropertyDB, BrowserMode


# -----------------------------------------------------------------------------------


# get connection string from .env file
DATABASE_URL: str | None = os.getenv('DATABASE_URL')

PROXY_USER: str | None = os.getenv('PROXY_USER')
PROXY_PASSWORD: str | None = os.getenv('PROXY_PASSWORD')
PROXY_IP: str | None = os.getenv('PROXY_IP')
PROXY_PORT: str | None = os.getenv('PROXY_PORT')

DRIVER_PATH: str | None = os.getenv('DRIVER_PATH')
LOG_FILE_PATH: str | None = os.getenv('LOG_FILE_PATH')

BROWSER_MODE_ENV: str = os.getenv('BROWSER_MODE', 'headless')

if BROWSER_MODE_ENV in get_args(BrowserMode):
    BROWSER_MODE = cast(BrowserMode, BROWSER_MODE_ENV)
else:
    BROWSER_MODE: BrowserMode = 'headless'


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
        # scr1.go_to_website(driver, wait, wait_time, ip_website_url)
        # brws.close_browser(driver)
        pass
    else:
        log.error(f"Cannot create driver and wait")

    return driver, wait





def scrape_p1(db: Session, session_id: UUID, session_name: str, 
            search_url: str, num_guest: int | None, num_property: int,
            save_db: bool = False
    ) -> List[PropertyDB]:
    
    driver: WebDriver | None = None
    wait: WebDriverWait | None = None
    driver, wait = start_driver()

    # --------------------------------

    if driver and wait:
        pass
    else:
        log.error(f"Failed to start driver and create wait object")
        return []

    # --------------------------------

    log.info(f'Search mode: {search_mode}')

    
    scr1.go_to_website(driver, wait, wait_time, search_url)

    # tool search
        # scr1.go_to_website(driver, wait, wait_time, main_website_url, view='main_page')
        # match search_mode:
        #     case 'none':
        #         pass
        #     case 'apply':
        #         scr1.search_location(driver, wait_time, location)
        #         scr1.search_date(driver, wait_time)
        #         scr1.search_guest(driver, wait_time, num_guest)
        #         scr1.press_search(driver)

    link_list: List[Dict[str, str]] = scr1.view_page_get_all_link(driver, wait, wait_time, num_property, search_mode)

    brws.close_browser(driver)
    
    # --------------------------------

    if not link_list:
        log.error(f"link_list is empty: {link_list}")
        return []
    
    # --------------------------------

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
            log.info(f'Saved property <{prop.prop_code}> (basic info) to database')
        
        link_list_db.append(prop)

    # --------------------------------

    if save_db and link_list_db:
        try: 
            db.commit()
            log.info(f'Batch saved {len(link_list_db)} properties (basic info) to database')

            # update prop object in Python with data created by db after the commit (eg: timestamp)
            for prop in link_list_db:
                db.refresh(prop)

        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to batch save properties (basic info) to database')
            db.rollback()
            return []

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
    batch_size: int = 10    # saved to db after every 10 properties

    # --------------------------------

    for idx, prop in enumerate[PropertyDB](detail_list_db, start=1):

        if shared_state.cancel_status:
            lg.log_divider('User trigger cancellation from FE -> cancel scraping process')
            break

        # --------------------------------

        lg.log_divider()
        log.info(f'Scraping property #{idx}: {prop.prop_code} - {prop.prop_name}')
        property_link: str = str(prop.prop_link)

        # --------------------------------

        try:
            scr1.go_to_website(driver, wait, wait_time, property_link, view='detail_page')
        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to access page of property <{prop.prop_code}> -> skip to next property')
            continue

        # --------------------------------

        try:
            overview_data: Dict[str, Any] = scr2.overview_info(driver, wait)
            for key, value in overview_data.items():
                setattr(prop, key, value)

            # --------------------------------

            rating_data: Dict[str, Any] = scr2.rating_info(driver)
            for key, value in rating_data.items():
                setattr(prop, key, value)

            # --------------------------------

            price_data: int | None = scr3.price_info(driver, wait_time)
            setattr(prop, 'nightly_price', price_data)

            # --------------------------------

            if collect_host_data:
                host_data: Dict[str, Any] = scr2.host_info(driver)
                for key, value in host_data.items():
                    setattr(prop, key, value)

            # --------------------------------

            if collect_booking_rate:
                book_rate_data: Dict[str, Any] = scr3.book_rate_info(driver, wait_time)
                for key, value in book_rate_data.items():
                    setattr(prop, key, value)

            # --------------------------------

            scrape_result: ScrapeResult = scr2.get_scrape_result(prop)
            setattr(prop, 'scrape_result', str(scrape_result)) 

            # --------------------------------

            log.info(f'Complete scraping data for property #{prop.prop_code} | result: {scrape_result}')
            scraped_prop_cnt += 1

        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to scrape all data of property <{prop.prop_code}> -> save already-scraped data to database')

        # --------------------------------

        if save_db and (idx % batch_size == 0 or idx == len(detail_list_db)):
            try:
                db.commit()
                batch_saved_cnt: int = idx - saved_prop_cnt
                saved_prop_cnt += batch_saved_cnt
                log.info(f'Saved {batch_saved_cnt} properties (detail info) to database')
            except Exception as e:
                lg.log_detail_error(e)
                log.error(f'Error to batch save property (detail info) to database')
                db.rollback()   # clean up failed transaction (eg: failed commit)

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
        file_name: str, search_url: str, num_guest: int | None, num_property: int,
        collect_host_data: bool = False,
        collect_booking_rate: bool = False
    ) -> ScrapeStatus:

    lg.log_divider('Start full flow')

    log.info("API Request Received:")
    log.info(f"""
    - file_name: {file_name}
    - search_url: {search_url}
    - Number of guests: {num_guest}
    - Number of properties: {num_property}
    - Collect host data: {collect_host_data}
    - Collect booking rate: {collect_booking_rate}
    """)

    # --------------------------------

    session_id: UUID = uuid4()
    session_name: str = dbop.get_session_name(db, file_name)
    log.info(f"New scraping session <{session_name}> started | ID: {session_id}")

    # --------------------------------

    link_list_db: List[PropertyDB] = scrape_p1(db, session_id, session_name, search_url, num_guest, num_property, save_db)
    log.info(f"Phase 1 (link scraping) completed.")

    if not link_list_db:
        log.error(f"Phase 1 didn't find any properties -> Stop scraping process")
        return ScrapeStatus.failed

    # --------------------------------

    if scrape_phase == 1 and not shared_state.cancel_status:
        scrape_status = ScrapeStatus.partial
    else:
        scrape_status: ScrapeStatus = scrape_p2(db, link_list_db, collect_host_data, collect_booking_rate, save_db)
        log.info(f"Phase 2 (detail scraping) completed.")
    
    # --------------------------------

    return scrape_status



# -----------------------------------------------------------------------------------

if test_local:
    if __name__ == "__main__":
        db_session: Session | None = dbop.create_db_session()

        log.info(f"""Config:
        - save_db: {save_db}
        - search_mode: {search_mode}
        - BROWSER_MODE: {BROWSER_MODE}
        - log_error_level: {log_error_level}
        """)

        if db_session:
            try: 
                run_full_flow(
                    db = db_session,
                    file_name = 'D2_HCM',
                    search_url = 'https://www.airbnb.com.vn/s/Ch%E1%BB%A3-B%E1%BA%BFn-Th%C3%A0nh--H%E1%BB%93-Ch%C3%AD-Minh/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJTeYpMT8vdTERMH8sUnkta40&acp_id=b3099460-7cf8-426d-a28d-2fd63584ecca&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&query=Ch%E1%BB%A3%20B%E1%BA%BFn%20Th%C3%A0nh%2C%20H%E1%BB%93%20Ch%C3%AD%20Minh&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2025-11-01&monthly_length=3&monthly_end_date=2026-02-01&search_mode=regular_search&price_filter_input_type=2&channel=EXPLORE&ne_lat=10.776167541325885&ne_lng=106.69584543240717&sw_lat=10.773755161532563&sw_lng=106.69300269380926&zoom=19.4407356826498&zoom_level=19.4407356826498&search_by_map=true&price_filter_num_nights=5&disable_auto_translation=true',
                    num_guest = None,
                    num_property = 1,
                    collect_host_data = True,
                    collect_booking_rate = True
                )
            finally:
                log.info("Closing database session for direct file run.")
                db_session.close()

        else:  
            log.error("Could not create database session.")



# search thẳng
        # move ad checking lên go_to_website
        # add website_url input 
    # sửa typing
    # sửa api
    # sửa FE


    