import re
import json
import logging
import requests
import datetime


import src.tool.utils as utl
from selenium.webdriver.remote.webdriver import WebDriver


# -----------------------------------------------------------------------------------

log = logging.getLogger(__name__)



def get_api_key(driver: WebDriver) -> str:
    """
    operation: scan source code to find api key
    output: api key
    """

    try:
        page_source = driver.page_source

        match = re.search(r'"key"\s*:\s*"([a-zA-Z0-9]{32})"', page_source)

        if match:
            return match.group(1)
        else:
            log.error(f"No api key found in page source")
            return "d306zoyjsyarp7ifhu67rjxn52tv0t20"

    except Exception as e:
        log.error(f"Error getting api key: {e}")
        return "d306zoyjsyarp7ifhu67rjxn52tv0t20"



def extract_authen_session(driver: WebDriver, api_key: str) -> requests.Session:

    session = requests.Session()

    # ------------------------

    selenium_coookies = driver.get_cookies()
    for cookie in selenium_coookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # ------------------------

    headers = {
        'x-airbnb-api-key': api_key,
        'content-type': 'application/json',
        'user-agent': driver.execute_script("return navigator.userAgent;"),

        'x-csrf-without-token': '1', 
        'x-airbnb-graphql-platform': 'web',
        'x-airbnb-graphql-platform-client': 'minimalist-niobe',
        'referer': driver.current_url,
    }
    session.headers.update(headers)

    return session



def get_listing_id_from_url(url: str) -> str | None:
    """
    Extracts the listing ID from an Airbnb URL.
    Example: https://www.airbnb.com/rooms/12345678?start=... -> 12345678
    """
    # Matches /rooms/ followed by digits
    match = re.search(r'/rooms/(\d+)', url)
    
    if match:
        listing_id = match.group(1) # (1) -> return first (...) group from re.search()
        log.info(f"Listing ID found in URL: {listing_id}")
        return listing_id
        
    return None



def test_calendar_api(session: requests.Session, listing_id: str):

    base_url = 'https://www.airbnb.com.vn/api/v3/PdpAvailabilityCalendar'
    sha_hash = '8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade'
    date_now = datetime.datetime.now()

    # ------------------------

    variables_dict = {
        "request": {
            "count": 3, #num of months
            "listingId": listing_id,
            "month": date_now.month,
            "year": date_now.year
        }
    }
    
    extensions_dict = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": sha_hash
        }
    }

    params = {
        "operationName": "PdpAvailabilityCalendar",
        "locale": "vi",
        "currency": "VND",
        "variables": json.dumps(variables_dict),
        "extensions": json.dumps(extensions_dict)
    }

    log.info(f"Testing API for Listing ID: {listing_id}...")

    try:
        response = session.get(base_url, params=params)
        
        if response.status_code == 200:
            log.info("✅ Calendar API SUCCESS")
            data = response.json()
            utl.print_pretty_dict(data)
            return data.get('data', {}).get('pdpAvailabilityCalendar', {})
    
        else:
            log.error(f"❌ Calendar API FAILED | status code: {response.status_code}")
            log.error(f"Response: {response.text[:500]}")
            return {}
            
    except Exception as e:
        log.error(f"❌ Calendar API Exception: {e}")
        return {}