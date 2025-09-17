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
import app.tool.file_op as fop
import app.detail_step.browser as brws
import app.detail_step.scrape_p1 as scr1
import app.detail_step.scrape_p2 as scr2
import app.detail_step.calculation as cal
import app.detail_step.dashboard as dshb
import app.tool.log_op as lg
import app.tool.db_op as dbop
import app.tool.utils as utl

from app.tool.config import proxy_user, proxy_password, proxy_ip, proxy_port
from app.tool.config import driver_path, wait_time
from app.tool.config import main_website_url, ip_website_url

from app.type.data import ScrapeResult, PropertyDB, ScrapeStatus
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
        log.error(f"An error in 'if driver'")
        return []

    scr1.go_to_website(driver, wait, wait_time, main_website_url, view='main_page')


    search: Literal['apply', 'none'] = 'none'
    log.info(f'Search mode: {search}')

    match search:
        case 'none':
            pass
        case 'apply':
            scr1.search_location(driver, wait_time, location)
            scr1.search_date(driver, wait_time)
            scr1.search_guest(driver, wait_time, num_guest)
            scr1.press_search(driver)

    link_list: List[Dict[str, str]] = scr1.view_page_get_all_link(driver, wait, wait_time, num_property, search)

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
        log.error(f"An error in 'if driver'")
        return ScrapeStatus.partial

    try:
        for prop in detail_list_db:

            log.info(f'Scraping property: {prop.prop_code} - {prop.prop_name}')

            property_link: str = str(prop.prop_link)
            scr1.go_to_website(driver, wait, wait_time, property_link, view='detail_page')

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

                log.info(f'Complete scraping property {prop.prop_code} - {prop.prop_name} | result: {scrape_result}')

            except Exception as e:
                lg.log_detail_error(e)
                log.error(f'Error in scraping property detail -> skip property {prop.prop_code} - {prop.prop_name}')

            if save_db:
                db.commit()
                log.info(f'Saved property <{prop.prop_code}> (detail info) to database')

            lg.log_divider()
            utl.print_pretty_dict(prop)

        lg.log_divider()
        log.info(f'Finish saving {len(detail_list_db)} properties (detail info) to database')
        log.info(f"Scraping process completed | {len(detail_list_db)} properties scraped")
        brws.close_browser(driver)
        lg.log_divider()

        return ScrapeStatus.success
    
    except Exception as e:
        lg.log_detail_error(e)
        log.error(f'Error in scraping property detail -> skip property {prop.prop_code} - {prop.prop_name}')
        return ScrapeStatus.partial




# def calculate_data(csv_path):
#     full_df = fop.csv_to_df(csv_path, index='prop_code', mode=2)
#     cnt_rating_cate_df = cal.cnt_rating_categories(full_df)
#     return cnt_rating_cate_df



# def draw_dashboard(csv_path, cal_data):
    
#     full_df = fop.csv_to_df(csv_path, index='prop_code', mode=2)

#     fig, axes = plt.subplots(2, 3, figsize=(15, 10))
#     axes_list = axes.flatten()

#     dshb.util_num_rating_star(axes_list[0], full_df)
#     dshb.rating_category_ratio(axes_list[1], cal_data)
#     dshb.rating_num_rating_star(axes_list[2], full_df)
#     dshb.this_month_BR_rating_star(axes_list[3], full_df)
#     dshb.next_1month_BR_rating_star(axes_list[4], full_df)
#     dshb.next_3month_BR_rating_star(axes_list[5], full_df)

#     plt.tight_layout()
#     plt.show()



# -----------------------------------------------------------------------------------



def run_full_flow(
        db: Session,
        file_name: str, location: str, num_guest: int, num_property: int,
        collect_host_data: bool = False,
        collect_booking_rate: bool = False,
        save_db: bool = False
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


# if __name__ == "__main__":
#     db_session: Session | None = dbop.create_db_session()

#     if db_session:
#         try: 
#             run_full_flow(
#                 db = db_session,
#                 file_name = 'PhoCo',
#                 location = 'Pho Co, hanoi',
#                 num_guest = 2,
#                 num_property = 1,
#                 collect_host_data = True,
#                 collect_booking_rate = True,
#                 save_db = True
#             )
#         finally:
#             log.info("Closing database session for direct file run.")
#             db_session.close()

#     else:  
#         log.error("Could not create database session.")



# # start_driver()

# print(f'\nLog file saved to: {log_file_path}\n')