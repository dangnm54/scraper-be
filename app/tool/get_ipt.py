import logging
from typing import Dict, Any, List
from datetime import date, datetime, timedelta

try:
    import app.tool.log_op as lg
    import app.tool.utils as utl
except ImportError:
    import tool.log_op as lg
    import tool.utils as utl


# from dateutil.relativedelta import relativedelta


# -----------------------------------------------------------------------------------

# lg.setup_logging_for_file_directly_run()

log = logging.getLogger(__name__)


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
        today_month: int = today_date.month
        next_1m_month: int = today_month + 1
        next_3m_month: List[int] = [next_1m_month, next_1m_month + 1, next_1m_month + 2]

        month_data['this_month'] = today_month
        month_data['next_1_month'] = next_1m_month
        month_data['next_3_month'] = next_3m_month

        log.info(f'Month data: {month_data}')

        return month_data


