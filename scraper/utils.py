import os
import json
import time
import unicodedata
import pandas as pd

import inspect
import sys
import traceback

from config import wait_time, data_folder_path
from datetime import datetime
from selenium.webdriver.common.by import By


# -----------------------------------------------------------------------------------


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



def list_dict_to_df(list_dict, index='ID'):
    df = pd.DataFrame(list_dict)
    df.set_index(index, inplace=True)

    print('List_of_dict -> Dataframe successful')
    print('-'*30)
    return df



def merge_df(df1, df2):
    merged_df = df1.merge(df2, left_index=True, right_index=True, how='left')
    
    print(f'Successfully merge Dataframe <{df1}> and Dataframe <{df2}>')
    print('-'*30)
    return merged_df    



def df_to_csv(df, name=None):
    folder_name = data_folder_path

    current_time = datetime.now().strftime('%d_%m')
    csv_name = f'{name}_{current_time}.csv'

    full_csv_path = os.path.join(folder_name, csv_name)
    os.makedirs(folder_name, exist_ok=True) #crt folder if not exist
    
    try:
        df.to_csv(full_csv_path, index=True, encoding='utf-8-sig')
        print(f'Dataframe saved to file: {full_csv_path}')
    except Exception as e:
        log_error(e)

    print('-'*30)
    return full_csv_path



def csv_to_df(csv_path, index=None, mode=1):
    match mode:
        case 1:
            df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig')
        case 2:
            df = pd.read_csv(csv_path, index_col=index, encoding='utf-8-sig', 
                dtype={
                'This_month_booked_rate': float,
                'Last_1_month_booked_rate': float,
                'Last_3_month_booked_rate': float,
                'Next_1_month_booked_rate': float,
                'Next_3_month_booked_rate': float, 
                })
    
    print(f'Dataframe created from file: {csv_path}')
    print('-'*30)
    return df



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

        return clean_string
    
    except Exception as e:
        log_error(e)
        return None



def scroll_focus_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)



def print_pretty_dict(dict):
    print(json.dumps(dict, indent=4, ensure_ascii=False))





