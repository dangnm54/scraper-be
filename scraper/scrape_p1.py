try:
    import scraper.utils as utl
except ImportError:
    import utils as utl

import time
import inspect

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------------------------------------------------------------


def go_to_website(driver, wait, wait_time, website_url, view=None):
    try:
        driver.get(website_url)
        print(f'Go to website: {website_url}')
        
        time.sleep(wait_time)

        #close ads if any
        try:
            ad_element1 = driver.find_element(By.CSS_SELECTOR, 'div.c1qme1pd')
            if EC.visibility_of(ad_element1):
                print('Found Ad pop-up')
                ok_button = ad_element1.find_element(By.CSS_SELECTOR, 'button')
                ok_button.click()
                print('Close Ad pop-up')
        except:
            pass

        try:
            ad_element2 = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Dịch trên"]')
            if EC.visibility_of(ad_element2):
                print('Found Ad pop-up')
                ok_button = ad_element2.find_element(By.CSS_SELECTOR, 'button[aria-label="Đóng"]')
                ok_button.click()
                print('Close Ad pop-up')
        except:
            pass

        match view:
            case 'main_page':
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main.m1un5iz5')))
            case 'detail_page':
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-section-id="HIGHLIGHTS_DEFAULT"]')))
        time.sleep(wait_time)
        

        # original_tab_handle = driver.current_window_handle
        # print(f'Handle <{original_tab_handle}> is for URL:{website_url}')
        # print('-'*30)

        # return original_tab_handle

    except Exception as e:
        utl.log_error(e)




# def check_proxy_ip(driver, wait, wait_time, website_url, original_tab_handle):
    # try:
    #     driver.execute_script(f"window.open('{website_url}', '_blank');")   # _blank means open in new tab

    #     all_tab_handle = driver.window_handles
    #     new_tab_handle = None
    #     for tab in all_tab_handle:
    #         if tab != original_tab_handle:
    #             new_tab_handle = tab
    #             print(f'Handle <{new_tab_handle}> is for URL:{website_url}')
    #             print('-'*30)
    #             break
        
    #     if new_tab_handle:
    #         driver.switch_to.window(new_tab_handle)
    #         print(f'Switched to {website_url}')

    #         wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'p.heading-xl.mb-4')))
    #         time.sleep(wait_time)
            
    #         ip_tag = driver.find_element(By.CSS_SELECTOR, 'p.heading-xl.mb-4')
    #         provider_tag = driver.find_element(By.CSS_SELECTOR, 'p.body-md-medium.mb-6')
    #         print(f'Proxy IP: {ip_tag.text} | Provider: {provider_tag.text}')

    #         driver.close()
    #         print('Close current tab')
    #         print('-'*30)

    #     driver.switch_to.window(original_tab_handle)
    #     print('Switched back to orginal tab')
    #     print('-'*30)
    
    # except Exception as e:
    #     utl.log_error(e)




def search_location(driver, wait_time, location_ipt):
    try:
        location_element = driver.find_element(By.CSS_SELECTOR, 'div.f1o8nkkf.atm_mk_h2mmj6.atm_wq_cs5v99')
        location_element.click()

        print('Location element found and clicked')
        time.sleep(wait_time)

        location_input = location_element.find_element(By.CSS_SELECTOR, 'input.fp9kp52')
        location_input.send_keys(location_ipt, Keys.ENTER)
        
        print(f'<{location_ipt}> typed and ENTER')
        time.sleep(wait_time)
        print('-'*30)
        
    except Exception as e:
        utl.log_error(e)



def search_date(driver, wait_time):
    try:
        flexible_date_button = driver.find_element(By.CSS_SELECTOR,'button[id="tab--tabs--2"]')
        flexible_date_button.click()

        print('Flexible time button found and clicked')
        time.sleep(wait_time)

        weekend_date_button = driver.find_element(By.CSS_SELECTOR,'label[id="flexible_trip_lengths-weekend_trip"]')
        weekend_date_button.click()
        
        print('Flexible weekend button found and clicked')
        time.sleep(wait_time)

        print('-'*30)

    except Exception as e:
        utl.log_error(e)



def search_guest(driver, wait_time, num_guest):
    try:
        date_guest_elements = driver.find_elements(By.CSS_SELECTOR,'div.fbb0tkq')
        for element in date_guest_elements:
            if element.text == 'Thêm khách':
                element.click()

        print('Guest element found and clicked')
        time.sleep(wait_time)

        guest_section = driver.find_element(By.CSS_SELECTOR,'div.p1nt1a2q')
        adult_element = guest_section.find_element(By.CSS_SELECTOR,'div[data-testid="search-block-filter-stepper-row-adults"]')
        add_button = adult_element.find_element(By.CSS_SELECTOR, 'button[aria-label="tăng giá trị"]')
                
        num_click = 0
        while num_click < num_guest:
            add_button.click()
            num_click += 1

        print(f'{num_guest} guests added')
        time.sleep(wait_time)

        print('-'*30)           

    except Exception as e:
        utl.log_error(e)



def press_search(driver):
    try:
        search_button = driver.find_element(By.CSS_SELECTOR,'button.siey6h7')
        search_button.click()

        print('Seach button founded and clicked')
        print('-'*30)

    except Exception as e:
        utl.log_error(e)



def view_page_get_all_link(driver, wait, wait_time, num_property):
    try:
        property_link_list = []
        property_count = 0 

        print(f'Ready to scrape {num_property} properties')
        print('-'*30)

        while property_count < num_property:
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,'div.cy5jw6o')))
            time.sleep(wait_time)

            property_section = driver.find_element(By.CSS_SELECTOR,'div.gsgwcjk')
            property_lists = property_section.find_elements(By.CSS_SELECTOR,'div.c965t3n')

            for property in property_lists:

                utl.scroll_focus_element(driver, property)

                property_info = {
                    'ID': 0,
                    'Name': '',
                    'Link': ''
                }

                name_element = property.find_element(By.CSS_SELECTOR,'span[data-testid="listing-card-name"]')
                name = name_element.text 
                link_element = property.find_element(By.CSS_SELECTOR,'div[data-testid="card-container"] > a')
                link = link_element.get_attribute('href')
                clean_link = utl.clean_text(link, mode=5)
                
                property_info['ID'] = property_count + 1
                property_info['Name'] = name
                property_info['Link'] = clean_link
                property_link_list.append(property_info)
                
                print(property_info)
                print('-'*20)

                property_count += 1

                if property_count == num_property:
                    break

            if property_count == num_property:
                    break
            else:
                try:
                    pagination_section = driver.find_element(By.CSS_SELECTOR, 'div.p1j2gy66')
                    next_page_element = pagination_section.find_element(By.CSS_SELECTOR, 'a[aria-label="Tiếp theo"]')
                    next_page_element.click()
                    print('Move to next page')
                    print('-'*30)
                except Exception as e:
                    print(f'On last page, no more property to scrape | {e}')
                    print('-'*30)
                    break

        print(f'{property_count} properties scraped')
        print('-'*30)
        return property_link_list

    except Exception as e:
        utl.log_error(e)
