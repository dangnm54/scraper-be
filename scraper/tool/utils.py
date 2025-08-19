import json
import time
import logging
import unicodedata
import random
import string
import datetime
from uuid import UUID
from typing import List, Dict, Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

try:
    import scraper.tool.log_op as lg
    from scraper.tool.config import wait_time
    from scraper.type.data import PropertyDB
except ImportError:
    import log_op as lg
    from config import wait_time
    from type.data import PropertyDB



# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)


def get_info_from_string(string: str, mode: str) -> str | int | None:

    try:
        word_list: List[str] = string.split()
        target_word: str | int | None = ''

        match mode:
            case 'int':
                for word in word_list:
                    # print(word)
                    if word.isdigit():
                        target_word = int(word)
                        # print(target_word)
                        
            case 'exp':
                for word in word_list:
                    # print(word)
                    if word.isdigit():
                        target_word = word
                    elif word == 'tháng':
                        target_word += ' thang'
                    elif word == 'năm':
                        target_word += ' nam'
                # print(target_word)

            case 'coordinate':
                word_list = word_list[0].split('/')
                for word in word_list:
                    if '@' in word:
                        raw_coordinate = word
                coordinate_point_list = raw_coordinate.strip('@').strip('z').split(',')
                target_word = ','.join(coordinate_point_list[0:2])

            case 'month':
                for word in word_list:
                    if word.isdigit() and int(word) < 2025:
                        # print(f'word: {word}')
                        target_word = int(word)
                
        return target_word
    
    except Exception as e:
        lg.log_detail_error(e)
        return None



def clean_text(string: str, mode: int) -> str:
    
    try:
        match mode:
            case 1:
                nfd_string: str = unicodedata.normalize('NFD', string)
                clean_text: str = ''.join(char for char in nfd_string if unicodedata.category(char) != 'Mn')

                replacements = {
                    'đ': 'd', 'Đ': 'D',
                    'ă': 'a', 'Ă': 'A',
                    'â': 'a', 'Â': 'A',
                    'ê': 'e', 'Ê': 'E',
                    'ô': 'o', 'Ô': 'O',
                    'ơ': 'o', 'Ơ': 'O',
                    'ư': 'u', 'Ư': 'U',
                }

                for vn_key, en_value in replacements.items():
                    clean_text = clean_text.replace(vn_key, en_value).lower()
            
            case 2:
                clean_text: str = string.strip('"').strip(' · ').lower()
            case 3:
                clean_text: str = (string.replace(',','.'))
            case 4:
                clean_text: str = string.replace('.','')
            case 5:
                clean_text: str = string.split('?')[0]

        return clean_text
    
    except Exception as e:
        lg.log_detail_error(e)
        return ''



def scroll_focus_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)



def print_pretty_dict(data: Dict[str, Any] | PropertyDB) -> None:

    dict_data: Dict[str, Any] = {}

    if isinstance(data, PropertyDB):
        for key, value in data.__dict__.items():
            # Skip SQLAlchemy internal attributes
            if not key.startswith('_'):
                if isinstance(value, UUID) or isinstance(value, datetime.datetime):
                    dict_data[key] = str(value)
                else:
                    dict_data[key] = value

    else:
        dict_data = data

    log.info(json.dumps(dict_data, indent=4, ensure_ascii=False))



def generate_random_id() -> str:
    """
    Generate a random ID in format P-XXXXXX
    X is a random uppercase letter or number
    """

    char_list: str = string.ascii_uppercase + string.digits
    random_id: str = ''.join(random.choice(char_list) for _ in range(6))
    
    return f"P-{random_id}"


