import os
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict

import scraper.tool.log_op as lg
import scraper.tool.utils as utl

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


# -----------------------------------------------------------------------------------

log = logging.getLogger(__name__)





def go_to_website(driver: WebDriver, wait_time: float, web_url: str) -> None:

    lg.log_divider('Go to website')

    try:
        driver.get(web_url)
        log.info(f'Go to website: {web_url}')
        time.sleep(wait_time)

    except Exception as e:
        log.error(f"An error in 'go_to_website': {e}")





def search(driver: WebDriver, wait_time: float, location_ipt: str, industry_ipt: str) -> None:

    lg.log_divider('Search')

    try:
        search_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'input.searchboxinput')
        log.info('Search element found')
        
        search_element.send_keys(location_ipt, Keys.ENTER)
        log.info(f'<{location_ipt}> typed and ENTER')

        time.sleep(wait_time)

        search_element.clear()
        search_element.send_keys(industry_ipt, Keys.ENTER)
        log.info(f'<{industry_ipt}> typed and ENTER')
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)





def scrape_data(driver: WebDriver, wait_time: float, num_data: int) -> List[Dict[str, str | None]]:

    lg.log_divider('Scrape data')

    log.info(f'Ready to scrape {num_data} data')

    client_data_list: List[Dict[str, str | None]] = []

    cnt = 0
    last_len = 0

    try:
        result_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb[role="feed"]')

        while cnt < num_data:

            result_list: List[WebElement] = result_section.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
            log.info(f'last_len: {last_len} | new_len: {len(result_list)}')

            new_data: int = len(result_list) - last_len

            lg.log_divider()
            if len(result_list) > last_len:
                log.info(f'{new_data} new data found -> keep scraping')
                last_len = len(result_list)
                pass
            else:
                log.info(f'{new_data} new data found -> stop scraping')
                break
            

            for client in result_list[cnt:]:

                lg.log_divider()
                log.info(f'Scraping data #{cnt}')

                client_data: Dict[str, str | None] = {
                    'code': utl.generate_random_code(),
                    'name': None,
                    'address': None,
                    'phone': None,
                    'ggmap_link': None
                }

                try:

                    utl.scroll_focus_element(driver, client)

                    client.click()
                    log.info('Data element clicked')
                    time.sleep(wait_time)

                    detail_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.bJzME.Hu9e2e')

                    # ----------------------------------------------------------

                    name_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'h1.DUwDvf')
                    name: str = name_element.text
                    log.info(f'Name: {name}')
                    client_data['name'] = name

                    # ----------------------------------------------------------

                    address_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'button.CsEnBe[data-tooltip="Copy address"]')
                    utl.scroll_focus_element(driver, address_element)
                    address: str = address_element.find_element(By.CSS_SELECTOR, 'div.Io6YTe').text
                    log.info(f'Address: {address}')
                    client_data['address'] = address

                    # ----------------------------------------------------------

                    phone_element: List[WebElement] = detail_section.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-tooltip="Copy phone number"]')
                    if phone_element:
                        utl.scroll_focus_element(driver, phone_element[0])
                        phone_num: WebElement = phone_element[0].find_element(By.CSS_SELECTOR, 'div.Io6YTe')
                        phone: str | None = phone_num.text
                    else:
                        phone = None
                    log.info(f'Phone: {phone}')
                    client_data['phone'] = phone

                    # ----------------------------------------------------------

                    share_button: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'button.g88MCb[data-value="Share"]')
                    utl.scroll_focus_element(driver, share_button)
                    share_button.click()
                    time.sleep(wait_time)
                    log.info('Share button clicked')

                    link_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'input.vrsrZe')
                    link: str | None = link_element.get_attribute('value')
                    log.info(f'Link: {link}')

                    close_button: WebElement = driver.find_element(By.CSS_SELECTOR, 'button.OyzoZb')
                    close_button.click()
                    log.info('Close share modal')
                    client_data['ggmap_link'] = link

                    
                except Exception as e:
                    lg.log_detail_error(e)
                    log.info(f'Error scraping data #{cnt} -> Skip to next data')

                    
                utl.print_pretty_dict(client_data)
                client_data_list.append(client_data)

                cnt += 1
                log.info(f'Data collected: {len(client_data_list)} | Total data needed: {num_data}')
                
                if cnt == num_data:
                    break
                else:
                    continue

            if cnt == num_data:
                break

        log.info(f'Scraping completed | Data collected: {len(client_data_list)}')
        return client_data_list


    except Exception as e:
        lg.log_detail_error(e)
        return client_data_list




def list_dict_to_csv(client_list: List[Dict[str, str | None]], name: str) -> str:

    lg.log_divider('Save to csv')

    folder_name: str = r'C:\Users\ADMIN\Pictures'
    current_time: str = datetime.now().strftime('%d%m%y')
    base_csv_name: str = f'{name}_{current_time}.csv'
    
    counter: int = 1
    csv_name: str = base_csv_name
    while os.path.exists(os.path.join(folder_name, csv_name)):
        name_without_ext: str = base_csv_name.replace('.csv', '')
        csv_name: str = f'{name_without_ext} ({counter}).csv'
        counter += 1

    full_csv_path: str = os.path.join(folder_name, csv_name)
    os.makedirs(folder_name, exist_ok=True) #crt folder if not exist
    
    # ----------------------------------------------------------

    with open(full_csv_path, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=client_list[0].keys())
        writer.writeheader()
        writer.writerows(client_list)

    log.info(f'File saved to: {full_csv_path}')


    return full_csv_path



