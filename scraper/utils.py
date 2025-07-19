import json
import time
import unicodedata
import logging
import inspect
import sys
import traceback
from datetime import datetime

try:
    from scraper.config import wait_time
except ImportError:
    from config import wait_time



# -----------------------------------------------------------------------------------



def setup_logging_for_file_directly_run():

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open('./app.log', 'w') as f:
        f.write(f'LOG RECORDED AT: {current_time}\n\n')



    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('./app.log', mode='a')
    
    log_format = logging.Formatter(
        '%(asctime)s | %(module)s - %(funcName)s - %(lineno)d | %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)



def log_error(e):

    print(f'Error start @ Function: {inspect.currentframe().f_back.f_code.co_name} | {e}\n')

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_info = traceback.extract_tb(exc_traceback)
    
    traceback_level = 3
    traceback_list = traceback_info[-traceback_level:]    # if requested level larger than actual list -> start from beginning of list
    
    for i, frame in enumerate(traceback_list):
        print(f'__Error level #{i+1}__')
        print(f'- Function: {frame.name}\n- File: {frame.filename}\n- Line #{frame.lineno}: {frame.line}')
        print('-'*10)
    print('-'*30)



def get_info_from_string(string, mode='int'):
    try:
        word_list = string.split()
        target_word = None
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
        log_error(e)
        return None



def clean_text(string, mode=1):
    try:
        match mode:
            case 1:
                clean_string = string.strip('"').strip(' · ').lower()

            case 2:
                nfd_string = unicodedata.normalize('NFD', string)
                clean_string = ''.join(char for char in nfd_string if unicodedata.category(char) != 'Mn')

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
                    clean_string = clean_string.replace(vn_key, en_value).lower()

            case 3:
                clean_string = float(string.replace(',','.'))
            case 4:
                clean_string = string.replace('.','')
            case 5:
                clean_string = string.split('?')[0]


        return clean_string
    
    except Exception as e:
        log_error(e)
        return None



def scroll_focus_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)



def print_pretty_dict(dict):
    print(json.dumps(dict, indent=4, ensure_ascii=False))




