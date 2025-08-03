try:
    import scraper.tool.utils as utl
    import scraper.tool.log_op as lg
except ImportError:
    import tool.utils as utl
    import tool.log_op as lg

import time
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def go_to_website(driver, wait, wait_time, website_url, view=None):

    lg.log_divider('Go to website')

    try:
        driver.get(website_url)
        log.info(f'Go to website: {website_url}')
        
        time.sleep(wait_time)

        try:
            driver.find_element(By.CSS_SELECTOR, 'body')
        except:
            log.info('Page not loaded properly, refreshing...')
            driver.refresh()
            time.sleep(wait_time)

        #close ads if any
        try:
            ad_element1 = driver.find_element(By.CSS_SELECTOR, 'div.c1qme1pd')
            if EC.visibility_of(ad_element1):
                log.info('Found Ad pop-up')
                ok_button = ad_element1.find_element(By.CSS_SELECTOR, 'button')
                ok_button.click()
                log.info('Close Ad pop-up')
        except:
            pass

        try:
            ad_element2 = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Dịch trên"]')
            if EC.visibility_of(ad_element2):
                log.info('Found Ad pop-up')
                ok_button = ad_element2.find_element(By.CSS_SELECTOR, 'button[aria-label="Đóng"]')
                ok_button.click()
                log.info('Close Ad pop-up')
        except:
            pass

        match view:
            case 'main_page':
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.m1un5iz5')))
            case 'detail_page':
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-section-id="HIGHLIGHTS_DEFAULT"]')))
        time.sleep(wait_time)
        

        # original_tab_handle = driver.current_window_handle
        # print(f'Handle <{original_tab_handle}> is for URL:{website_url}')
        # print('-'*30)

        # return original_tab_handle

    except Exception as e:
        lg.log_detail_error(e)




# def check_proxy_ip(driver, wait, wait_time, website_url, original_tab_handle):

    # lg.log_divider('Check proxy IP')

    # try:
    #     driver.execute_script(f"window.open('{website_url}', '_blank');")   # _blank means open in new tab

    #     all_tab_handle = driver.window_handles
    #     new_tab_handle = None
    #     for tab in all_tab_handle:
    #         if tab != original_tab_handle:
    #             new_tab_handle = tab
    #             log.debug(f'Handle <{new_tab_handle}> is for URL:{website_url}')
    #             break
        
    #     if new_tab_handle:
    #         driver.switch_to.window(new_tab_handle)
    #         log.info(f'Switched to {website_url}')

    #         wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'p.heading-xl.mb-4')))
    #         time.sleep(wait_time)
            
    #         ip_tag = driver.find_element(By.CSS_SELECTOR, 'p.heading-xl.mb-4')
    #         provider_tag = driver.find_element(By.CSS_SELECTOR, 'p.body-md-medium.mb-6')
    #         log.info(f'Proxy IP: {ip_tag.text} | Provider: {provider_tag.text}')

    #         driver.close()
    #         log.info('Close current tab')

    #     driver.switch_to.window(original_tab_handle)
    #     log.info('Switched back to orginal tab')
    
    # except Exception as e:
        lg.log_detail_error(e)



def search_location(driver, wait_time, location_ipt):

    lg.log_divider('Search location')

    try:
        location_element = driver.find_element(By.CSS_SELECTOR, 'div.f1o8nkkf.atm_mk_h2mmj6.atm_wq_cs5v99')
        location_element.click()

        log.info('Location element found and clicked')
        time.sleep(wait_time)

        location_input = location_element.find_element(By.CSS_SELECTOR, 'input.fp9kp52')
        location_input.send_keys(location_ipt, Keys.ENTER)
        
        log.info(f'<{location_ipt}> typed and ENTER')
        time.sleep(wait_time)
        
    except Exception as e:
        lg.log_detail_error(e)



def search_date(driver, wait_time):

    lg.log_divider('Search date')

    try:
        flexible_date_button = driver.find_element(By.CSS_SELECTOR,'button[id="tab--tabs--2"]')
        flexible_date_button.click()

        log.info('Flexible time button found and clicked')
        time.sleep(wait_time)

        weekend_date_button = driver.find_element(By.CSS_SELECTOR,'label[id="flexible_trip_lengths-weekend_trip"]')
        weekend_date_button.click()
        
        log.info('Flexible weekend button found and clicked')
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)



def search_guest(driver, wait_time, num_guest):

    lg.log_divider('Search guest')

    try:
        date_guest_elements = driver.find_elements(By.CSS_SELECTOR,'div.fbb0tkq')
        for element in date_guest_elements:
            if element.text == 'Thêm khách':
                element.click()

        log.info('Guest element found and clicked')
        time.sleep(wait_time)

        guest_section = driver.find_element(By.CSS_SELECTOR,'div.p1nt1a2q')
        adult_element = guest_section.find_element(By.CSS_SELECTOR,'div[data-testid="search-block-filter-stepper-row-adults"]')
        add_button = adult_element.find_element(By.CSS_SELECTOR, 'button[aria-label="tăng giá trị"]')
                
        num_click = 0
        while num_click < num_guest:
            add_button.click()
            num_click += 1

        log.info(f'{num_guest} guests added')
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)



def press_search(driver):

    lg.log_divider('Press search')

    try:
        search_button = driver.find_element(By.CSS_SELECTOR,'button.siey6h7')
        search_button.click()

        log.info('Seach button founded and clicked')

    except Exception as e:
        lg.log_detail_error(e)



def view_page_get_all_link(driver, wait, wait_time, num_property):

    lg.log_divider('View page and get all link')

    try:
        property_link_list = []
        property_count = 0 

        log.info(f'Ready to scrape {num_property} properties')

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
                
                log.info(property_info)

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
                    log.info('Move to next page')
                    lg.log_divider()
                except Exception as e:
                    log.error(f'On last page, no more property to scrape | {e}')
                    lg.log_detail_error(e)
                    break

        log.info(f'{property_count} properties scraped')
        return property_link_list

    except Exception as e:
        lg.log_detail_error(e)
