import logging
from typing import Dict, Any, List

from selenium.webdriver.remote.webdriver import WebDriver

import src.tool.log_op as lg
import src.tool.utils as utl
import src.tool.api_op as api_op


# -----------------------------------------------------------------------------------


log = logging.getLogger(__name__)



def get_book_rate(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    - input: response (json) of 3 months
    - operation:extract book rate info from given response (json)
    """

    lg.log_divider('Book rate info')

    book_rate_data: Dict[str, Any] = {
        'this_month_booked_rate': None,  # Optional[float]
        'next_1_month_booked_rate': None,  # Optional[float]
        'next_3_month_booked_rate': None,  # Optional[float]
    }

    # ------------------------

    # utl.print_pretty_dict(response)

    try:

        month_list: List[Dict[str, Any]] = response.get('calendarMonths',[])

        cum_day: int = 0
        cum_booked: int = 0
        
        for idx, month in enumerate[Dict[str, Any]](month_list):
            
            month_name: str = month.get('month', '')
            log.info(f'Index #{idx}: month {month_name}')

            # ------------------------

            day_list: List[Dict[str, Any]] = month.get('days',[])
            
            day_cnt: int = len(day_list)
            # log.info(f'Total day count: {day_cnt}')
            
            booked_cnt: int = sum(1 for day in day_list if 
                day.get('available', False) == False and 
                day.get('availableForCheckout', False) == False
            )
            # log.info(f'Booked day count: {booked_day_cnt}')

            # ------------------------

            cum_day += day_cnt
            cum_booked += booked_cnt

            # ------------------------

            match idx:
                case 0:
                    book_rate_data['this_month_booked_rate'] = book_rate_cal(booked_cnt, day_cnt)
                case 1:
                    book_rate_data['next_1_month_booked_rate'] = book_rate_cal(booked_cnt, day_cnt)
                case 2:
                    book_rate_data['next_3_month_booked_rate'] = book_rate_cal(cum_booked, cum_day)

        # ------------------------

        utl.print_pretty_dict(book_rate_data)
        return book_rate_data

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_book_rate')
        return book_rate_data



def book_rate_cal(booked_day_cnt: int, day_cnt: int) -> float | None:
    book_rate: float | None = None
    try:
        book_rate = float(booked_day_cnt / day_cnt * 100)
        log.info(f'Total booked-rate: {booked_day_cnt} / {day_cnt} = {book_rate:.2f}%')
    except ZeroDivisionError:
        book_rate = None
        log.info('No data to calculate book_rate')

    return book_rate



def get_price(response: Dict[str, Any]) -> int | None:

    lg.log_divider('Price info')

    price_data: int | None = None

    # ------------------------

    try:    
        price_response = api_op.get_response_part(response, 'price')
        utl.print_pretty_dict(price_response)

    except Exception as e:
        lg.log_detail_error(e, 'Error in get_price')
        return price_data