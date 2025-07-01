import utils as utl          # import module from same directory (folder / package)
import get_ipt as ipt
import browser as brws
import scrape_p1 as scr1
import scrape_p2 as scr2
import calculation as cal
import dashboard as dshb

from config import proxy_user, proxy_password, proxy_ip, proxy_port
from config import driver_path, wait_time
from config import main_website_url, ip_website_url

import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------------


def scrape_p1(proxy_user, proxy_password, proxy_ip, proxy_port, driver_path,
            file_name: str, location: str, num_guest: int, num_property: int
    ):
    
    extension_dir = brws.crt_proxy_helper_extention(proxy_user, proxy_password, proxy_ip, proxy_port)
    options_1 = brws.config_basic_driver_setting()
    options_2 = brws.config_advanced_driver_setting(extension_dir, options_1)
    driver, wait = brws.start_browser(driver_path, options_2)

    if driver is None or wait is None:
        print(f"An error in 'if driver'")

    original_tab_handle = scr1.go_to_website(driver, wait, wait_time, main_website_url, view='main_page')
    # scr1.check_proxy_ip(driver, wait, wait_time, ip_website_url, original_tab_handle)

    scr1.search_location(driver, wait_time, location)
    scr1.search_date(driver, wait_time)
    scr1.search_guest(driver, wait_time, num_guest)
    scr1.press_search(driver)

    property_link_list = scr1.view_page_get_all_link(driver, wait, wait_time, num_property)
    property_link_df = utl.list_dict_to_df(property_link_list, index='ID')
    property_link_csv_path = utl.df_to_csv(property_link_df, name=f'{file_name}_link')

    brws.close_browser(driver)

    return property_link_csv_path





def scrape_p2(proxy_user, proxy_password, proxy_ip, proxy_port, driver_path, property_link_csv_path,
            file_name: str, collect_host_data: bool=False, collect_booking_rate: bool=False
    ):

    extension_dir = brws.crt_proxy_helper_extention(proxy_user, proxy_password, proxy_ip, proxy_port)
    options_1 = brws.config_basic_driver_setting()
    options_2 = brws.config_advanced_driver_setting(extension_dir, options_1)
    driver, wait = brws.start_browser(driver_path, options_2)

    property_link_df = utl.csv_to_df(property_link_csv_path, index='ID', mode=1)
    property_detail_list = []

    if driver is None or wait is None:
        print(f"An error in 'if driver'")

    for index, row in property_link_df.iterrows():
        # print(f'{index} | {row['Name']} | {row['Link']}')

        # if index < 8:
        #     continue

        property_detail_data = {
            'ID': index,
            'Scrape_status': None,

            'Guest_num': None,
            'Bed_num': None,
            'Bath_num': None,
            'Location': None,

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

            'Rating_title':None,
            'Rating_num': None,
            'Rating_star': None,
            # 'Rating_clean_score': None,
            # 'Rating_accuracy_score': None,
            # 'Rating_checkin_score': None,
            # 'Rating_commu_score': None,
            # 'Rating_location_score': None,
            # 'Rating_value_score': None,

            'Host_name': None,
            'Host_title': None,
            'Host_rating_star': None,
            'Host_rating_num': None,
            'Host_exp': None,
            'Host_link': None,

            # 'Co_host_num': None,
            # 'Co_host_name': None,
            # 'Co_host_link': None,

            'This_month_booked_rate': None,
            # 'Last_1_month_booked_rate': None,
            # 'Last_3_month_booked_rate': None,
            'Next_1_month_booked_rate': None,
            'Next_3_month_booked_rate': None, 
        } 

        print(f'Scraping property #{index} - {row["Name"]}')
        
        original_tab_handle = scr1.go_to_website(driver, wait, wait_time, row['Link'], view='detail_page')
        # scr1.check_proxy_ip(driver, wait, wait_time, ip_website_url, original_tab_handle)

        try:
            property_detail_data['Scrape_status'] = 'Success'
            
            overview_data = scr2.overview_info(driver, wait)
            property_detail_data.update(overview_data)

            # utility_data = scr2.utility_info(driver, wait_time)
            # property_detail_data.update(utility_data)
    
            rating_data = scr2.rating_info(driver)
            property_detail_data.update(rating_data)

            if collect_host_data:
                host_data = scr2.host_info(driver)
                property_detail_data.update(host_data)

            # co_host_data = scr2.co_host_info(driver)
            # property_detail_data.update(co_host_data)

            if collect_booking_rate:
                month_data = ipt.get_date_for_book_data()
                book_rate_data = scr2.book_rate_info(driver, wait_time, month_data)
                property_detail_data.update(book_rate_data)

        except Exception as e:
            utl.log_error(e)
            property_detail_data.update({'ID': index, 'Scrape_status':'Failed'})


        utl.print_pretty_dict(property_detail_data)
        print('-'*30)    
        property_detail_list.append(property_detail_data)

        # if index == 1:
        #     break

    brws.close_browser(driver)  

    property_detail_df = utl.list_dict_to_df(property_detail_list, index='ID') 
    property_full_df = utl.merge_df(property_link_df, property_detail_df)
    property_full_csv_path = utl.df_to_csv(property_full_df, name=f'{file_name}_full')
    return property_full_csv_path





def calculate_data(csv_path):

    property_full_df = utl.csv_to_df(csv_path, index='ID', mode=2)

    cnt_rating_cate_df = cal.cnt_rating_categories(property_full_df)

    return cnt_rating_cate_df





def draw_dashboard(csv_path, cal_data):
    
    property_full_df = utl.csv_to_df(csv_path, index='ID', mode=2)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes_list = axes.flatten()

    dshb.util_num_rating_star(axes_list[0], property_full_df)
    dshb.rating_category_ratio(axes_list[1], cal_data)
    dshb.rating_num_rating_star(axes_list[2], property_full_df)
    dshb.this_month_BR_rating_star(axes_list[3], property_full_df)
    dshb.next_1month_BR_rating_star(axes_list[4], property_full_df)
    dshb.next_3month_BR_rating_star(axes_list[5], property_full_df)

    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------------------------------



def run_full_flow(
        file_name: str,
        location: str,
        num_guest: int,
        num_property: int,
        collect_host_data: bool = False,
        collect_booking_rate: bool = False
):
    
    
    print("API Request Received")
    print(f"""
        - Location: {location}
        - Number of guests: {num_guest}
        - Number of properties: {num_property}
        - Collect host data: {collect_host_data}
        - Collect booking rate: {collect_booking_rate}
    """)


    try:
        property_link_csv_path = scrape_p1(
            proxy_user, proxy_password, proxy_ip, proxy_port, driver_path,
            file_name, location, num_guest, num_property
        )
        print(f"Phase 1 (link scraping) completed. File saved to: {property_link_csv_path}")
        # property_link_csv_path = r'D:\software\other\cursor\python\airbnb_proj\file\D3_link_20_05_final.csv'


        # property_full_csv_path = scrape_p2(
        #     proxy_user, proxy_password, proxy_ip, proxy_port, driver_path, property_link_csv_path,
        #     file_name, collect_host_data, collect_booking_rate
        # )
        # print(f"Phase 2 (detail scraping) completed. File saved to: {property_full_csv_path}")
        # # property_full_csv_path = r'D:\software\other\cursor\python\airbnb_proj\file\D3_full_03_06_final.csv'


        # # cal_data = calculate_data(property_full_csv_path)
        # # draw_dashboard(property_full_csv_path, cal_data)

        return {
            "status": "success",
            "message": "scraping process completed",
            "output_file": property_link_csv_path
        }


    except Exception as e:
        utl.log_error(e)
        return {
            "status": "error",
            "message": f"scraping process failed: {str(e)}"
        }




run_full_flow(
    file_name = 'HoTay_HN',
    location = 'Ho Tay, hanoi',
    num_guest = 2,
    num_property = 10,
    collect_host_data = True,
    collect_booking_rate = True
)







