import sys
import os
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import src.tool.log_op as lg
    from src.tool.config import wait_time
    from src.type.data import PropertyDB
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
                raw_coordinate: str = ''
                for word in word_list:
                    if '@' in word:
                        raw_coordinate = word
                coordinate_axis_list = raw_coordinate.strip('@').strip('z').split(',')
                target_word = ','.join(coordinate_axis_list[0:2])  # stop before position #2

            case 'ggmap_link':
                target_word = f'https://maps.google.com/?q={string}'

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
    
    clean_text: str = ''
    try:
        match mode:
            case 1:
                nfd_string: str = unicodedata.normalize('NFD', string)
                clean_text = ''.join(char for char in nfd_string if unicodedata.category(char) != 'Mn')

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
                clean_text = string.strip('"').strip(' · ').lower()
            case 3:
                clean_text = (string.replace(',','.'))
            case 4:
                clean_text = string.replace('.','')
            case 5:
                clean_text = string.split('?')[0]

        return clean_text
    
    except Exception as e:
        lg.log_detail_error(e)
        return ''



def scroll_focus_element(driver: WebDriver, element: WebElement) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)



def print_pretty_dict(data: Dict[str, Any] | PropertyDB) -> None:

    dict: Dict[str, Any] = {}

    if isinstance(data, PropertyDB):
        dict = obj_to_dict(data)
    else:
        dict = data

    log.info(json.dumps(dict, indent=4, ensure_ascii=False))



def obj_to_dict(obj: Any) -> Dict[str, Any]:

    dict: Dict[str, Any] = {}

    if not isinstance(obj, PropertyDB):
        log.info('Data is not <PropertyDB> object -> skip convert')
        return dict

    ordered_keys: List[str] = [col.name for col in obj.__table__.columns]

    for key in ordered_keys:
        value: Any = getattr(obj, key, None)
        if isinstance(value, (UUID, datetime.datetime)):
            dict[key] = str(value)
        else:
            dict[key] = value
            
    log.info(f'Success convert <PropertyDB> object -> <Dict> object')

    return dict



def generate_random_code() -> str:
    """
    Generate a random code in format P-XXXXXX
    X is a random uppercase letter or number
    """

    char_list: str = string.ascii_uppercase + string.digits
    random_id: str = ''.join(random.choice(char_list) for _ in range(6))
    
    return f"P-{random_id}"



