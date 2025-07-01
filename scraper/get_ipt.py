from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta


# -----------------------------------------------------------------------------------


def get_basic_search_info():
    print('--Search info--')
    # location = str(input('Location: '))
    # start_date = datetime(input('Start date: '))
    # end_date = datetime(input('Start date: '))
    # num_guest = int(input('Number of guests: '))
    # num_property = int(input('Number of property to scrape: '))

    # location = 'District 3, HCM'
    location = 'District 1, HCM'
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    num_guest = 2
    num_property = 5

    print(f'Location: {location}')
    print(f'Start date: {start_date.date()}')
    print(f'End date: {end_date.date()}')
    print(f'Number of guests: {num_guest}')
    print(f'Number of property to scrape: {num_property}')

    print('-'*30)
    return location, num_guest, num_property
    


def get_date_for_book_data():
        
        print('--Month info--')
    
        cal_data = {
            'This_month_booked_rate': None,
            # 'Last_1_month_booked_rate': None,
            # 'Last_3_month_booked_rate': None,
            'Next_1_month_booked_rate': None,
            'Next_3_month_booked_rate': None,
            'Avg_nightly_price': None            
        }
        
        today_date = datetime.now().date()        
        today_month = today_date.month

        # last_1m_date = today_date - relativedelta(months=1)
        # last_1m_month = last_1m_date.month
        # last_3m_month = [last_1m_month-2, last_1m_month-1, last_1m_month]

        next_1m_month = today_month + 1

        next_3m_month = [next_1m_month, next_1m_month+1, next_1m_month+2]

        print(f'today_month: {today_month}')
        # print(f'last_1m_month: {last_1m_month}')
        # print(f'last_3m_month: {last_3m_month}')
        print(f'next_1m_month: {next_1m_month}')
        print(f'next_3m_month: {next_3m_month}')
        print('-'*30)

        return today_month, next_1m_month, next_3m_month
