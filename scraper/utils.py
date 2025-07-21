import json
import time
import unicodedata

try:
    from scraper.config import wait_time
    import scraper.log_op as lg
except ImportError:
    from config import wait_time
    import log_op as lg



# -----------------------------------------------------------------------------------



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
        lg.log_detail_error(e)
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
        lg.log_detail_error(e)
        return None



def scroll_focus_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center', behavior:'smooth'});", element)
    time.sleep(wait_time)



def print_pretty_dict(dict):
    print(json.dumps(dict, indent=4, ensure_ascii=False))




