try:
    import scraper.utils as utl
except ImportError:
    import utils as utl

import time
import lxml

from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------------------------------------------------------------


# def get_soup_from_driver(driver): 
#     try:
#         html_content = driver.page_source
#         print('HTML content retrieved from driver')

#         soup = BeautifulSoup(html_content, 'lxml')
#         print('HTML content parsed')
        
#         print('-'*30)
#         return soup

#     except Exception as e:
#         utl.log_error(e)



def overview_info(driver, wait):
    try:
        overview_data = {
            'Guest_num': None,
            'Bed_num': None,
            'Bath_num': None,
            'Location': None
        }
    
        overview_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="OVERVIEW_DEFAULT_V2"]')
        print('Overview section found')

        info_list = overview_section.find_elements(By.CSS_SELECTOR, 'li.l7n4lsf')
        for info in info_list:
            clean_info1 = utl.clean_text(info.text, mode=1)
            clean_info2 = utl.clean_text(clean_info1, mode=2)

            num = utl.get_info_from_string(clean_info2, mode='int')

            if 'khach' in clean_info2:
                overview_data['Guest_num'] = num
            if 'giuong' in clean_info2:
                overview_data['Bed_num'] = num
            if 'tam' in clean_info2:
                overview_data['Bath_num'] = num

        location_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="LOCATION_DEFAULT"]')
        utl.scroll_focus_element(driver, location_section)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[title="Báo cáo lỗi trong bản đồ đường hoặc hình ảnh đến Google"]')))
        location_element = location_section.find_element(By.CSS_SELECTOR, 'a[title="Báo cáo lỗi trong bản đồ đường hoặc hình ảnh đến Google"]')
        location = location_element.get_attribute('href')
        clean_location = utl.get_info_from_string(location, 'coordinate')
        overview_data['Location'] = clean_location

        utl.print_pretty_dict(overview_data)
        print('-'*30)
        return overview_data
    
    except Exception as e:
        utl.log_error(e)
        return overview_data



def utility_info(driver, wait_time):
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

        utility_num = utl.get_info_from_string(utility_button.text, mode='int')
        utility_data['Utility_num'] = utility_num
        
        # utility_button.click()
        # time.sleep(wait_time)
        # print('Open utility modal')

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
        #     clean_cate_name = utl.clean_text(cate_name, mode=2)

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

        #     print(f'\nCategory: {clean_cate_name}')
        #     print(f'Item list: {item_list}')
        #     print('-'*10)
            
        # close_button = utility_modal.find_element(By.CSS_SELECTOR, 'button[aria-label="Đóng"]')
        # close_button.click()
        # print('Close modal')
        # print('-'*30)

        utl.print_pretty_dict(utility_data)
        print('-'*30)
        return utility_data

    except Exception as e:
        utl.log_error(e)
        return utility_data



def rating_info(driver):
    try:
        rating_data = {
            'Rating_title':None,
            'Rating_star': None,
            'Rating_num': None,
            # 'Rating_clean_score': None,
            # 'Rating_accuracy_score': None,
            # 'Rating_checkin_score': None,
            # 'Rating_commu_score': None,
            # 'Rating_location_score': None,
            # 'Rating_value_score': None,
        }

        # overview data
        overview_rating_special = driver.find_elements(By.CSS_SELECTOR, 'div[data-section-id="GUEST_FAVORITE_BANNER"]')
        overview_rating_normal = driver.find_elements(By.CSS_SELECTOR, 'div.rgr5sph')

        if overview_rating_special:
            overview_rating_special = overview_rating_special[0]
            utl.scroll_focus_element(driver, overview_rating_special)            
            print('Special rating element found')
            
            rating_title = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.lbjrbi0')
            clean_rating_title = rating_title.text.replace('\n',' ')
            rating_data['Rating_title'] = clean_rating_title

            rating_star_section = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.a8jhwcl')
            rating_star_elements = rating_star_section.find_elements(By.CSS_SELECTOR, 'div')
            rating_star = utl.clean_text(rating_star_elements[0].text, mode=3)
            rating_data['Rating_star'] = rating_star

            rating_num_section = overview_rating_special.find_element(By.CSS_SELECTOR, 'div.r16onr0j')
            rating_num_elements = rating_num_section.find_elements(By.CSS_SELECTOR, 'div')
            rating_num = int(rating_num_elements[0].text)
            rating_data['Rating_num'] = rating_num

            print('Special overview rating data collected')
            print('-'*30)
            
        elif overview_rating_normal:
            overview_rating_normal = overview_rating_normal[0]
            utl.scroll_focus_element(driver, overview_rating_normal)            
            print('Normal rating element found')

            rating_star = overview_rating_normal.find_element(By.CSS_SELECTOR, 'div.rmtgcc3')
            clean_rating_star = utl.clean_text(rating_star.text, mode=3)
            rating_data['Rating_star'] = clean_rating_star

            rating_num = overview_rating_normal.find_element(By.CSS_SELECTOR, 'a')
            clean_rating_num = utl.get_info_from_string(rating_num.text, mode='int')
            rating_data['Rating_num'] = clean_rating_num
            
            print('Normal overview rating data collected')
            print('-'*30)


        # detail data
        # rating_detail_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="REVIEWS_DEFAULT"]')
        # print('Rating section found')

        # rating_category_list = rating_detail_section.find_elements(By.CSS_SELECTOR, 'div.l925rvg')
        # for category in tqdm(rating_category_list, desc='Scraping rating detail data: '):
        #     utl.scroll_focus_element(driver, category)

        #     detail_element = category.find_elements(By.CSS_SELECTOR, 'div')
        #     category_name = utl.clean_text(detail_element[0].text, mode=2)
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

        #     print(f'\nCategory: {category_name}')
        #     print(f'Rating: {category_rating}')
        #     print('-'*10)

        utl.print_pretty_dict(rating_data)
        print('-'*30)
        return rating_data

    except Exception as e:
        utl.log_error(e)
        return rating_data    



def host_info(driver):
    try:
        host_data = {
            'Host_name': None,
            'Host_title': None,
            'Host_rating_num': None,
            'Host_rating_star': None,
            'Host_exp': None,
            'Host_link': None,
        }

        host_section = driver.find_element(By.CSS_SELECTOR, 'div.c1h2ee1b')
        utl.scroll_focus_element(driver, host_section)

        host_name = host_section.find_element(By.CSS_SELECTOR, 'span.t1gpcl1t').text
        host_data['Host_name'] = host_name

        host_title_element = host_section.find_elements(By.CSS_SELECTOR, 'span.s1h3l0w7')
        host_title = host_title_element[0].text
        if host_title != 'Host':
            host_data['Host_title'] = host_title

        host_detail_section = host_section.find_element(By.CSS_SELECTOR, 'div.s13au5n7')

        host_rating_num = host_detail_section.find_element(By.CSS_SELECTOR, 'span[data-testid="Đánh giá-stat-heading"]')
        clean_host_rating_num1 = utl.clean_text(host_rating_num.text, mode=4)
        clean_host_rating_num2 = utl.get_info_from_string(clean_host_rating_num1, mode='int')
        host_data['Host_rating_num'] = clean_host_rating_num2

        host_rating_star = host_detail_section.find_element(By.CSS_SELECTOR, 'div.rz5w5y3')
        clean_host_rating_star = utl.clean_text(host_rating_star.text, mode=3)
        host_data['Host_rating_star'] = clean_host_rating_star

        host_exp = host_detail_section.find_elements(By.CSS_SELECTOR, 'span.a8jt5op')
        if len(host_exp) ==3:
            host_exp_element = host_exp[2]
            clean_host_exp = utl.get_info_from_string(host_exp_element.text, mode='exp')
            host_data['Host_exp'] = clean_host_exp

        host_avatar = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Xem Hồ sơ đầy đủ của Chủ nhà/Người tổ chức"]')
        host_link = host_avatar.get_attribute('href')
        host_data['Host_link'] = host_link

        utl.print_pretty_dict(host_data)
        print('-'*30)
        return host_data

    except Exception as e:
        utl.log_error(e)
        return host_data



def co_host_info(driver):
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

                print(f'Co-host name: {name}')
                print(f'Co-host link: {link}')
                print('-'*10)

            co_host_data['Co_host_name'] = name_list
            co_host_data['Co_host_link'] = link_list

        else:
            co_host_data['Co_host_num'] = 0
            print('No co-host')

        utl.print_pretty_dict(co_host_data)
        print('-'*30)
        return co_host_data

    except Exception as e:
        utl.log_error(e)
        return co_host_data



def book_rate_info(driver, wait_time, month_data):
    try:
        book_rate_data = {
            'This_month_booked_rate': None,
            # 'Last_1_month_booked_rate': None,
            # 'Last_3_month_booked_rate': None,
            'Next_1_month_booked_rate': None,
            'Next_3_month_booked_rate': None,         
        }

        book_section = driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="BOOK_IT_SIDEBAR"]')
        utl.scroll_focus_element(driver, book_section)
        print('Book time section found')

        start_date_element = book_section.find_element(By.CSS_SELECTOR, 'div._19y8o0j')
        start_date_element.click()

        print('Open calender')
        print('-'*10)
        time.sleep(wait_time)
        
        today_month, next_1m_month, next_3m_month = month_data

        for month in month_data:
            print(f'\n_____Checking month <{month}>_____')
            # month = month_data[0]
        
            if type(month) == int:
                # continue
                target_month = month

                tot_date, booked_date = detail_booking_cal(driver, wait_time, target_month)

                book_rate = final_stage_book_cal(booked_date, tot_date)

                if month == month_data[0]:
                    book_rate_data['This_month_booked_rate'] = book_rate
                # elif month == month_data[1]:
                #     book_rate_data['Last_1_month_booked_rate'] = book_rate 
                elif month == month_data[1]:
                    book_rate_data['Next_1_month_booked_rate'] = book_rate 


            elif type(month) == list:
                target_month_range = month
                print(f'Target month list: {target_month_range}')

                all_tot_date = 0
                all_booked_date = 0
                
                for target_month in target_month_range:
                    print(f'Single target month: {target_month}')
                    single_tot_date, single_booked_date = detail_booking_cal(driver, wait_time, target_month)
                    all_tot_date += single_tot_date
                    all_booked_date += single_booked_date

                book_rate = final_stage_book_cal(all_booked_date, all_tot_date)

                # if target_month_range == month_data[2]:
                #     book_rate_data['Last_3_month_booked_rate'] = book_rate
                if target_month_range == month_data[2]:
                    book_rate_data['Next_3_month_booked_rate'] = book_rate 

        utl.print_pretty_dict(book_rate_data)
        print('-'*30)
        return book_rate_data

    except Exception as e:
        utl.log_error(e)



def final_stage_book_cal(booked_date, tot_date):
    try:
        book_rate = float(booked_date/tot_date*100)
        print(f'{booked_date} / {tot_date} = {book_rate:.2f}%')
    except ZeroDivisionError:
        book_rate = None
        print('No data to calculate book_rate')
    
    print('-'*30)
    return book_rate



def detail_booking_cal(driver, wait_time, target_month):
    try:
        max_try = 12
        current_try = 0
        while current_try < max_try:
            current_try += 1
            print(f'Try #{current_try}')

            calender_section = driver.find_elements(By.CSS_SELECTOR, 'div.c1e8f4ze')[1]
            button_section = calender_section.find_element(By.CSS_SELECTOR, 'div._5neba7a')
            last_month_button = button_section.find_element(By.CSS_SELECTOR, 'button[aria-label="Chuyển sang tháng trước."]')
            next_month_button = button_section.find_element(By.CSS_SELECTOR, 'button[aria-label="Di chuyển lên trên để chuyển sang tháng sau."]')

            month_sides = calender_section.find_elements(By.CSS_SELECTOR, 'div._1lds9wb') 
            month_pair = []

            for month_box in month_sides:
                month_name = month_box.find_element(By.CSS_SELECTOR, 'h3')

                # print(month_name.text)


                clean_month_name = utl.get_info_from_string(month_name.text, 'month')
                month_pair.append(clean_month_name)
            
            # print(f'Target month: {target_month}')
            # print(f'Current month_pair: {month_pair}')

            if target_month in month_pair:
                print('At the right calendar view')
                time.sleep(wait_time)
                print('-'*10)

                matched_month_box = month_sides[0] if target_month == month_pair[0] else month_sides[1]
                date_list = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[class]')
                booked_date_list = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="true"]')
                avai_date_list = matched_month_box.find_elements(By.CSS_SELECTOR, 'td[aria-disabled="true"]')

                tot_date = len(date_list)
                booked_date = len(booked_date_list)
                
                return tot_date, booked_date
            
            else:
                if target_month < month_pair[0]:

                    if last_month_button.is_enabled():
                        last_month_button.click()
                        print('Wrong calendar view -> last_month_button clicked')
                        time.sleep(wait_time)
                    else:
                        print('No more calender data visible to scrape')
                        print('-'*30)
                        return 0, 0

                elif target_month > month_pair[1]:
                    next_month_button.click()
                    print('Wrong calendar view -> next_month_button clicked')
                    time.sleep(wait_time)
                print('-'*10)

    except Exception as e:
        utl.log_error(e)
        return 0, 0
    



# -----------------------------------------------------------------------------------


# full detail data

# property_detail_data = {
#     'ID': index,
#     'Scrape_status': None,

#     'Guest_num': None,
#     'Bed_num': None,
#     'Bath_num': None,
#     'Location': None,

#     # 'Utility_num': None,
#     # 'Utility_bathroom': None,
#     # 'Utility_bedroom': None,
#     # 'Utility_entertain': None,
#     # 'Utility_safety': None,
#     # 'Utility_kitchen': None,
#     # 'Utility_outdoor': None,
#     # 'Utility_parking': None,
#     # 'Utility_service': None,
#     # 'Utility_not_included': None,

#     'Rating_title':None,
#     'Rating_num': None,
#     'Rating_star': None,
#     # 'Rating_clean_score': None,
#     # 'Rating_accuracy_score': None,
#     # 'Rating_checkin_score': None,
#     # 'Rating_commu_score': None,
#     # 'Rating_location_score': None,
#     # 'Rating_value_score': None,

#     'Host_name': None,
#     'Host_title': None,
#     'Host_rating_star': None,
#     'Host_rating_num': None,
#     'Host_exp': None,
#     'Host_link': None,

#     # 'Co_host_num': None,
#     # 'Co_host_name': None,
#     # 'Co_host_link': None,

#     'This_month_booked_rate': None,
#     # 'Last_1_month_booked_rate': None,
#     # 'Last_3_month_booked_rate': None,
#     'Next_1_month_booked_rate': None,
#     'Next_3_month_booked_rate': None, 
# } 





