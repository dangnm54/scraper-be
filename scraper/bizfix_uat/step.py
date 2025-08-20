import logging
import time
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

        search_element.send_keys(industry_ipt, Keys.ENTER)
        log.info(f'<{industry_ipt}> typed and ENTER')
        time.sleep(wait_time)

    except Exception as e:
        lg.log_detail_error(e)





def scrape_data(driver: WebDriver, wait_time: float, num_data: int) -> List[Dict[str, str | None]]:

    lg.log_divider('Scrape data')

    log.info(f'Ready to scrape {num_data} data')

    try:
        result_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb[role="feed"]')
        
        client_data_list: List[Dict[str, str | None]] = []

        cnt = 0

        while cnt < num_data:

            result_list: List[WebElement] = result_section.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
            
            len_list = len(result_list)
            last_position = len_list -1

            for client in result_list:

                client_data: Dict[str, str | None] = {
                    'code': utl.generate_random_code(),
                    'name': None,
                    'address': None,
                    'phone': None,
                    'ggmap_link': None
                }

                utl.scroll_focus_element(driver, client)

                client.click()
                log.info('Data element clicked')
                time.sleep(wait_time)

                detail_section: WebElement = driver.find_element(By.CSS_SELECTOR, 'div.bJzME.Hu9e2e')

                name_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'h1.DUwDvf')
                name: str = name_element.text
                log.info(f'Name: {name}')


                address_element: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'button.CsEnBe[data-tooltip="Copy address"]')
                utl.scroll_focus_element(driver, address_element)
                address: str = address_element.find_element(By.CSS_SELECTOR, 'div.Io6YTe').text
                log.info(f'Address: {address}')


                phone_element: List[WebElement] = detail_section.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-tooltip="Copy phone number"]')
                if phone_element:
                    utl.scroll_focus_element(driver, phone_element[0])
                    phone_num: WebElement = phone_element[0].find_element(By.CSS_SELECTOR, 'div.Io6YTe')
                    phone: str | None = phone_num.text
                else:
                    phone = None
                log.info(f'Phone: {phone}')


                share_button: WebElement = detail_section.find_element(By.CSS_SELECTOR, 'button.g88MCb[data-value="Share"]')
                utl.scroll_focus_element(driver, share_button)
                share_button.click()
                time.sleep(wait_time)
                log.info('Share button clicked')

                link_element: WebElement = driver.find_element(By.CSS_SELECTOR, 'input.vrsrZe')
                link: str | None = link_element.get_attribute('value')
                log.info(f'Link: {link}')


                client_data['name'] = name
                client_data['address'] = address
                client_data['phone'] = phone
                client_data['ggmap_link'] = link

                utl.print_pretty_dict(client_data)

                client_data_list.append(client_data)

                cnt += 1
                if cnt == num_data:
                    break

            if cnt == num_data:
                break

        return client_data_list









    except Exception as e:
        lg.log_detail_error(e)
        return []
