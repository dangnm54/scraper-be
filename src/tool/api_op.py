import re
import json
import base64
import logging
import requests
import urllib.parse
import datetime
from typing import Dict, Any


import src.tool.utils as utl
import src.tool.log_op as lg
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





def get_authen_session(driver: WebDriver, api_key: str) -> requests.Session:

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





def get_input_from_url(url: str) -> Dict[str, Any]:
    """
    Extracts the (1) listing ID and (2) chosen dates from an Airbnb URL.
    Example: https://www.airbnb.com.vn/rooms/1470103827296390049?source_impression_id=p3_1764337132_P3_cA2KuJQDwWvaV&check_in=2025-12-02&guests=1&adults=1&check_out=2025-12-03
    """

    lg.log_divider('get_input_from_url')
    log.info(f"Extracting listing ID and dates from URL: {url}")

    input_data: Dict[str, Any] = {
        'listing_id': None,
        'checkin_date': None,
        'checkout_date': None
    }
    
    # ------------------------

    input_map = [
        {
            'key': 'listing_id',
            'regex': r'/rooms/(\d+)',
        },
        {
            'key': 'checkin_date',
            'regex': r'check_in=(\d{4}-\d{2}-\d{2})',
        },
        {
            'key': 'checkout_date',
            'regex': r'check_out=(\d{4}-\d{2}-\d{2})',
        }
    ]

    # ------------------------

    for input in input_map:
        match = re.search(input['regex'], url)
        if match:
            info = match.group(1)
            input_data[input['key']] = info

    # ------------------------

    utl.print_pretty_dict(input_data)
    return input_data





def get_host_id_from_response(response: Dict[str, Any]) -> int:

    lg.log_divider('get_host_id_from_response')

    host_overview_resp: Dict[str, Any] = get_response_part(response, 'host')
    host_id: int = host_overview_resp.get('hostAvatar', {}).get('loggingEventData', {}).get('eventData', {}).get('pdpContext', {}).get('hostId', 0)
    
    log.info(f'Host ID: {host_id}')
    return host_id





def get_response_part(response: Dict[str, Any], part_name: str) -> Dict[str, Any]:

    # log.info('response')
    # utl.print_pretty_dict(response)

    part_response: Dict[str, Any] = {}
    prop_detail_outer_layers = response.get('data',{}).get('presentation',{}).get('stayProductDetailPage',{}).get('sections',{})

    # log.info('PropDetail_outer_layers')
    # utl.print_pretty_dict(prop_detail_outer_layers)

    match part_name:
        case 'price':
            part_response = prop_detail_outer_layers.get('sections',[])[1].get('section',{}).get('structuredDisplayPrice',{})
        case 'location':
            part_response = prop_detail_outer_layers.get('sections',[])[0].get('section',{})
        case 'overview':
            part_response = prop_detail_outer_layers.get('sbuiData',{}).get('sectionConfiguration',{}).get('root',{}).get('sections',[])[0].get('sectionData',{})
        case 'host':
            part_response = prop_detail_outer_layers.get('sbuiData',{}).get('sectionConfiguration',{}).get('root',{}).get('sections',[])[1].get('sectionData',{})



    return part_response





def call_calendar_api(session: requests.Session, listing_id: str) -> Dict[str, Any]:

    lg.log_divider('call_calendar_api')

    # ------------------------

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

    # ------------------------

    log.info(f"Fetching API for Listing ID: {listing_id}...")

    try:
        response = session.get(base_url, params=params)
        
        if response.status_code == 200:
            log.info("✅ Calendar API SUCCESS")

            resp: Dict[str, Any] = response.json()
            # utl.print_pretty_dict(resp)

            need_data: Dict[str, Any] = resp.get('data',{}).get('merlin',{}).get('pdpAvailabilityCalendar',{})
            # utl.print_pretty_dict(need_data)
            
            return need_data

        else:
            log.error(f"❌ Calendar API FAILED | status code: {response.status_code}")
            log.error(f"Response: {response.text[:500]}")
            return {}
            
    except Exception as e:
        log.error(f"❌ Calendar API Exception: {e}")
        return {}



def call_prop_detail_api(
    session: requests.Session, listing_id: str,
    checkin_date: str, checkout_date: str
) -> Dict[str, Any]:

    lg.log_divider('call_prop_detail_api')

    # ------------------------

    base_url = 'https://www.airbnb.com.vn/api/v3/PdpAvailabilityCalendar'
    sha_hash = '4171aca8c004aa2347b2ffa286d67e3c81f53ae0bc11f7fba721a1c163fe0f46'

    id_val = base64.b64encode(f"StayListing:{listing_id}".encode()).decode()
    demand_id_val = base64.b64encode(f"DemandStayListing:{listing_id}".encode()).decode()

    # ------------------------

    variables_dict = {
        "id": id_val,
        "demandStayListingId": demand_id_val,
        "pdpSectionsRequest": {
            "adults": "1",
            "bypassTargetings": False,
            "layouts": ["SIDEBAR", "SINGLE_COLUMN"],
            "pets": 0,
            "checkIn": checkin_date,
            "checkOut": checkout_date,
            "sectionIds": [
                "OVERVIEW_DEFAULT_V2",      # has: Guests, Beds, Ratings
                "HOST_OVERVIEW_DEFAULT",    # has: Host Name, Experience
                "BOOK_IT_SIDEBAR",          # has: pricing
                "DESCRIPTION_DEFAULT",      # has: Full text description
                "LOCATION_DEFAULT"          # has: Map/Location info
                # "AMENITIES_DEFAULT",
                # "POLICIES_DEFAULT",       # has: Check-in/out times
            ],
            "p3ImpressionId": "p3_1764299520_P3fY8_xX8vE13gpf"
        },
        "useContextualUser": True,
        "includeHotelFragments": False,
        "includePdpMigrationFragments": False,
        "includeGpTitleFragment": True
    }

    extensions_dict = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": sha_hash
        }
    }

    params = {
        "operationName": "StaysPdpSections",
        "locale": "vi",
        "currency": "VND",
        "variables": json.dumps(variables_dict),
        "extensions": json.dumps(extensions_dict)
    }

    # ------------------------

    log.info(f"Fetching PropertyDetail API for Listing ID: {listing_id}...")

    try:
        response = session.get(base_url, params=params)
        
        if response.status_code == 200:
            log.info("✅ PropertyDetail API SUCCESS")

            resp: Dict[str, Any] = response.json()
            # utl.print_pretty_dict(resp)
            
            return resp

        else:
            log.error(f"❌ PropertyDetail API FAILED | status code: {response.status_code}")
            log.error(f"Response: {response.text[:500]}")
            return {}
            
    except Exception as e:
        log.error(f"❌ PropertyDetail API Exception: {e}")
        return {}





def call_host_api(session: requests.Session, host_id: int) -> Dict[str, Any]:

    lg.log_divider('call_host_api')

    # ------------------------

    base_url = 'https://www.airbnb.com.vn/api/v3/ContextualPublicProfileQuery'
    sha_hash = 'e5be5314e402c6e215ee97b8584e02044115be7978555232e1b9fcaa8ca202cc'

    contextual_user_id_raw = f"ContextualUser:{host_id}"
    contextual_user_id = base64.b64encode(contextual_user_id_raw.encode()).decode()

    # ------------------------

    viewer_user_id = ''
    is_viewer_logged_in = False

    try:
        user_attributes = session.cookies.get('_user_attributes')
        if user_attributes:
            decoded_attrs = urllib.parse.unquote(user_attributes)
            user_data = json.loads(decoded_attrs)
            
            if 'id' in user_data:
                raw_viewer_id = f"User:{user_data['id']}"
                viewer_user_id = base64.b64encode(raw_viewer_id.encode()).decode()
                is_viewer_logged_in = True
                log.info(f"Found logged-in viewer ID: {user_data['id']}")
    except Exception as e:
        log.warning(f"Could not extract viewer info from cookies: {e}")

    # ------------------------

    variables = {
        "contextualUserId": contextual_user_id,
        "viewerUserId": viewer_user_id,
        "isViewerLoggedIn": is_viewer_logged_in
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": sha_hash
        }
    }

    params = {
        "operationName": "ContextualPublicProfileQuery",
        "locale": "vi",
        "currency": "VND",
        "variables": json.dumps(variables),
        "extensions": json.dumps(extensions)
    }

    # ------------------------

    try:
        response = session.get(base_url, params=params)
        
        if response.status_code == 200:
            log.info("✅ Host API SUCCESS")

            resp: Dict[str, Any] = response.json()
            # utl.print_pretty_dict(resp)
            return resp

        else:
            log.error(f"❌ Host API FAILED | status code: {response.status_code}")
            log.error(f"Response: {response.text[:500]}")
            return {}
            
    except Exception as e:
        log.error(f"❌ Host API Exception: {e}")
        return {}
    