import time
import logging
from typing import List, Dict, Literal, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import src.tool.utils as utl
import src.tool.log_op as lg
import src.detail_step.shared_state as shared_state


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def go_to_website(driver: WebDriver, wait: WebDriverWait, wait_time: float, website_url: str, view: str | None = None) -> None:

    lg.log_divider('Go to website')

    try:
        driver.get(website_url)
        log.info(f'Go to website: {website_url}')
        
        time.sleep(wait_time)

        # --------------------------------

        try:
            driver.find_element(By.CSS_SELECTOR, 'body')
            log.info('Page loaded properly')
        except:
            log.info('Page not loaded properly, refreshing...')
            driver.refresh()
            time.sleep(wait_time)

        # --------------------------------

        ad_css_configs: List[Dict[str, Any]] = [
            {
                'type': 'main-page',
                'element': 'div[aria-label="Giờ đây bạn sẽ thấy một mức giá duy nhất cho chuyến đi của mình, đã bao gồm mọi khoản phí."]',
                'ok_button':'button[aria-label="Đóng"]'
            },
            {
                'type': 'result-search-page',
                'element': 'div.c1qme1pd',
                'ok_button':'button[aria-label="Đóng"]'
            },
            {
                'type': 'detail-page',
                'element': 'div[aria-label="Dịch trên"]',
                'ok_button':'button[aria-label="Đóng"]'
            }
        ]

        # --------------------------------

        try:
            log.info('Check Ad pop-up')

            all_element_css: str = ",".join([config['element'] for config in ad_css_configs])

            ad_element: WebElement = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, all_element_css)))
            log.info('Found Ad pop-up')

            # --------------------------------

            found_config: Dict[str, Any] | None = None

            for config in ad_css_configs:
                config_elements: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, config['element'])
                log.info(f'Check config | found_element: <{ad_element}> | current_elements: <{config_elements}>')
                if ad_element in config_elements:
                    found_config = config
                    log.info(f'Found ad type <{config["type"]}>')
                    break

            # --------------------------------

            if found_config:
                ok_button: WebElement = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, found_config['ok_button'])))
                log.info('Found close button')
                ok_button.click()
                log.info('Close Ad pop-up')
            else:
                log.error('Cannot identify ad type')

            # --------------------------------

        except TimeoutException:
            log.error(f'Found no Ad pop-up')

        except Exception as e:
            lg.log_detail_error(e)
            log.error(f'Error to locate and close Ad pop-up | {e}')
            pass


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



def search_location(driver: WebDriver, wait_time: float, location_ipt: str) -> None:

    lg.log_divider('Search location')

    try:
        location_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.f1o8nkkf.atm_mk_h2mmj6.atm_wq_cs5v99')
        location_element.click()

        log.info('Location element found and clicked')
        time.sleep(wait_time)

        location_input: WebElement = location_element.find_element(By.CSS_SELECTOR, 'input.fp9kp52')
        location_input.send_keys(location_ipt, Keys.ENTER)
        
        log.info(f'<{location_ipt}> typed and ENTER')
        time.sleep(wait_time)
        
    except Exception as e:
        lg.log_detail_error(e)



def search_date(driver: WebDriver, wait_time: float) -> None:

    lg.log_divider('Search date')

    try:
        flexible_date_button: WebElement = driver.find_element(By.CSS_SELECTOR,'button[id="tab--tabs--2"]')
        flexible_date_button.click()

        log.info('Flexible time button found and clicked')
        time.sleep(wait_time)

        weekend_date_button: WebElement = driver.find_element(By.CSS_SELECTOR,'label[id="flexible_trip_lengths-weekend_trip"]')
        weekend_date_button.click()
        
        log.info('Flexible weekend button found and clicked')
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)



def search_guest(driver: WebDriver, wait_time: float, num_guest: int | None) -> None:

    lg.log_divider('Search guest')

    if num_guest is None:
        log.info('Search without guest number')
        time.sleep(wait_time)
        return

    try:
        date_guest_elements: List[WebElement] = driver.find_elements(By.CSS_SELECTOR,'div.fbb0tkq')
        for element in date_guest_elements:
            if element.text == 'Thêm khách':
                element.click()

        log.info('Guest element found and clicked')
        time.sleep(wait_time)

        guest_section: WebElement = driver.find_element(By.CSS_SELECTOR,'div.p1nt1a2q')
        adult_element: WebElement = guest_section.find_element(By.CSS_SELECTOR,'div[data-testid="search-block-filter-stepper-row-adults"]')
        add_button: WebElement = adult_element.find_element(By.CSS_SELECTOR, 'button[aria-label="tăng giá trị"]')

        num_click: int = 0
        while num_click < num_guest:
            add_button.click()
            num_click += 1

        log.info(f'{num_guest} guests added')
        time.sleep(wait_time)


    except Exception as e:
        lg.log_detail_error(e)



def press_search(driver: WebDriver) -> None:

    lg.log_divider('Press search')

    try:
        search_button: WebElement = driver.find_element(By.CSS_SELECTOR,'button.siey6h7')
        search_button.click()

        log.info('Seach button founded and clicked')

    except Exception as e:
        lg.log_detail_error(e)



def view_page_get_all_link(driver: WebDriver, wait: WebDriverWait, wait_time: float, num_property: int, search: Literal['apply', 'none']) -> List[Dict[str, str]]:
    
    lg.log_divider('View page and get all link')

    # --------------------------------

    try:
        log.info(f'Ready to scrape {num_property} properties | Search-mode: {search}')

        link_list: List[Dict[str, str]] = []
        prop_cnt: int = 0

        while prop_cnt < num_property:

            prop_list: List[WebElement] = []
            try:
                match search:
                    case 'none':
                        prop_list = driver.find_elements(By.CSS_SELECTOR,'div.c1r8sk5a')

                    case 'apply':
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.c965t3n')))
                        time.sleep(wait_time)
                        prop_list = driver.find_elements(By.CSS_SELECTOR,'div.cfutgp0')
            except Exception as e:
                lg.log_detail_error(e)
                log.error(f'Error to check visibility and locate property list | {e}')
                break

            # --------------------------------

            for property in prop_list:

                if shared_state.cancel_status:
                    lg.log_divider('User trigger cancellation from FE -> cancel scraping process')
                    break

                # -------------------------------

                utl.scroll_focus_element(driver, property)

                prop_info: Dict[str, str] = {
                    'prop_code': '',
                    'prop_name': '',
                    'prop_link': ''
                }

                # --------------------------------

                match search:
                    case 'none':
                        name_element: WebElement = property.find_element(By.CSS_SELECTOR,'div[data-testid="listing-card-title"]')
                    case 'apply':
                        name_element = property.find_element(By.CSS_SELECTOR,'span[data-testid="listing-card-name"]')
                name: str = name_element.text 

                # --------------------------------
                
                link_element: WebElement = property.find_element(By.CSS_SELECTOR,'div[data-testid="card-container"] > a')
                link: str | None = link_element.get_attribute('href')
                if link:
                    clean_link: str = utl.clean_text(link, mode=5)
                else:
                    clean_link = ''
                
                # --------------------------------

                prop_info['prop_code'] = utl.generate_random_code()
                prop_info['prop_name'] = name
                prop_info['prop_link'] = clean_link

                # --------------------------------

                link_list.append(prop_info)
                prop_cnt += 1

                log.info(f'Prop #{prop_cnt} / {num_property}: {name}')
                utl.print_pretty_dict(prop_info)

                # --------------------------------

                if prop_cnt == num_property:
                    break

            # --------------------------------

            if prop_cnt == num_property:
                    break
            else:
                try:
                    pagination_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.p1j2gy66')
                    next_page_element: WebElement = pagination_section.find_element(By.CSS_SELECTOR, 'a[aria-label="Tiếp theo"]')
                    next_page_element.click()
                    time.sleep(wait_time)
                    log.info('Move to next page')
                    lg.log_divider()
                except Exception as e:
                    log.error(f'On last page, no more property to scrape | {e}')
                    lg.log_detail_error(e)
                    break

            # --------------------------------

        log.info(f'{prop_cnt} properties (basic info) scraped')
        return link_list

    except Exception as e:
        lg.log_detail_error(e)
        return []
