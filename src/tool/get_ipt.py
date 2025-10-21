import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import logging
import src.tool.log_op as lg

if __name__ == "__main__":
    log_file_path = lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------


from typing import Dict, Any, List
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import src.tool.log_op as lg
import src.tool.utils as utl


# -----------------------------------------------------------------------------------


def get_basic_search_info() -> Dict[str, Any]:
    
    log.info('Search info')
    
    search_info: Dict[str, Any] = {
        'location': None,
        'start_date': None,
        'end_date': None,
        'num_guest': None,
        'num_property': None
    }
    
    # location = str(input('Location: '))
    # start_date = datetime(input('Start date: '))
    # end_date = datetime(input('Start date: '))
    # num_guest = int(input('Number of guests: '))
    # num_property = int(input('Number of property to scrape: '))

    location = 'District 1, HCM'
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    num_guest = 2
    num_property = 5

    log.info(f'Search info: {utl.print_pretty_dict(search_info)}')

    lg.log_divider()

    return search_info
    


def get_date_for_book_data() -> Dict[str, Any]:
        
        log.info('--Month info--')

        month_data: Dict[str, Any] = {
            'this_month': None, # int
            'next_1_month': None, # int
            'next_3_month': None, # List[int]
        }
        
        today_date: date = datetime.now().date()
        next_1m_date: date = today_date + relativedelta(months=1)
        next_2m_date: date = today_date + relativedelta(months=2)
        next_3m_date: date = today_date + relativedelta(months=3)

        month_data['this_month'] = int(today_date.month)
        month_data['next_1_month'] = int(next_1m_date.month)
        month_data['next_3_month'] = [int(next_1m_date.month), int(next_2m_date.month), int(next_3m_date.month)]

        log.info(f'Month data:')
        utl.print_pretty_dict(month_data)

        return month_data
