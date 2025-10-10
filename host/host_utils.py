import sys
import os
import time
import json
import logging
from typing import List, Dict, Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import src.tool.log_op as lg
from src.tool.config import wait_time

# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def clean_string(string: str, mode: str) -> str:

    try:
        word_list: List[str] = string.split()
        target_word: str = ''

        match mode:
            case 'rating_star':
                # no space -> not split
                # test -> ' "4,94" '
                word: str = word_list[0]
                word = word.strip('"').replace(',', '.')
                target_word = word

            case 'exp_unit':
                # test: "năm kinh nghiệm đón tiếp khách"
                for word in word_list:
                    if word in ['Tháng', 'tháng']:
                        target_word = ' thang'
                        break
                    elif word in ['Năm', 'năm']:
                        target_word = ' nam'
                        break

            case 'prop_num':
                # test: "Xem tất cả 13 bài đăng"
                for word in word_list:
                    if word.isdigit():
                        target_word = word
                        break

            case 'rv_star':
                # test: "Xếp hạng trung bình 4,98/5, 130 đánh giá"
                for word in word_list:
                    if '/' in word:
                        target_word = word.replace('/5,', '').replace(',', '.')
                        break

        return target_word

    except Exception as e:
        lg.log_detail_error(e)
        return ''





def pretty_dict(data: Dict[str, Any]) -> None:
    dict: Dict[str, Any] = data
    log.info(json.dumps(dict, indent=4, ensure_ascii=False))





def scroll_focus_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)