import sys
import os
import time
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import src.tool.log_op as lg
from src.tool.config import wait_time

# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)

DATA_FOLDER_PATH: str | None = os.getenv('DATA_FOLDER_PATH')


# -----------------------------------------------------------------------------------



def clean_string(string: str, mode: str) -> str:

    try:
        word_list: List[str] = string.split()
        target_word: str = ''
        word: str = ''
        # print(f'word_list: {word_list}')

        match mode:
            case 'rating_num':
                word = word_list[0]
                target_word = word.replace('.', '').strip('\n+')

            case 'rating_star':
                # test: "Mới"
                # test: ' "4,94" '
                word = word_list[0]
                if 'Mới' in word:
                    target_word = '0'
                else:
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
                # test: 
                    # "Xem tất cả 13 bài đăng"
                    # "Nơi ở mới"
                for word in word_list:
                    if 'mới' in word:
                        target_word = '0'
                        break
                    if word.isdigit():
                        target_word = word
                        break

            # case 'rv_star':
            #     # test: 
            #         # "Xếp hạng trung bình 4,98/5, 130 đánh giá"
            #         # "Mới"
            #     for word in word_list:
            #         if 'Mới' in word:
            #             target_word = '0'
            #             break
            #         if '/' in word:
            #             target_word = word.replace('/5,', '').replace(',', '.')
            #             break

        return target_word

    except Exception as e:
        lg.log_detail_error(e)
        return ''





def df_to_csv(df: pd.DataFrame, name: str) -> str:
    folder_name: str | None = DATA_FOLDER_PATH
    if folder_name:
        pass
    else:
        log.error(f"DATA_FOLDER_PATH is not set")
        return ""

    # make file name
    current_time: str = datetime.now().strftime('%d%m%y')
    base_csv_name: str = f'{name}_{current_time}.csv'
    
    counter: int = 1
    csv_name: str = base_csv_name
    while os.path.exists(os.path.join(folder_name, csv_name)):
        name_without_ext: str = base_csv_name.replace('.csv', '')
        csv_name = f'{name_without_ext} ({counter}).csv'
        counter += 1

    full_csv_path: str = os.path.join(folder_name, csv_name)
    os.makedirs(folder_name, exist_ok=True) #crt folder if not exist
    
    # convert to csv
    try:
        df.to_csv(full_csv_path, index=True, encoding='utf-8-sig')
        log.info(f'Dataframe saved to file: {full_csv_path}')
    except Exception as e:
        lg.log_detail_error(e)

    return full_csv_path





def pretty_dict(data: Dict[str, Any]) -> None:
    dict: Dict[str, Any] = data
    log.info(json.dumps(dict, indent=4, ensure_ascii=False))





def scroll_focus_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)