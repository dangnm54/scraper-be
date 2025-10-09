import sys
import os
import json
import logging
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import src.tool.log_op as lg

# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)




def clean_string(string: str, mode: str) -> str:

    try:
        word_list: List[str] = string.split()
        target_word: str = ''

        match mode:
            case 'rating_num':
                # no space -> not split
                word: str = word_list[0]
                word = word.strip('"').replace(',', '')
                target_word = word

            case 'exp_unit':
                for word in word_list:
                    if word == 'Tháng':
                        target_word = 'thang'
                        break
                    elif word == 'Năm':
                        target_word = 'nam'
                        break    
                target_word = '(unknown unit)'

        return target_word


    except Exception as e:
        lg.log_detail_error(e)
        return ''





def pretty_dict(data: Dict[str, Any]) -> None:
    dict: Dict[str, Any] = data
    log.info(json.dumps(dict, indent=4, ensure_ascii=False))