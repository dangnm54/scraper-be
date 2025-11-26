import random

from src.type.data import BrowserMode, SearchMode, LogErrorLevel


# ------------------------------------------------------------


# wait time: 2 - 4s
wait_time: float = random.uniform(1, 2) + random.uniform(1, 2) - random.uniform(0.1, 0.5)


# website links
main_website_url: str = 'https://www.airbnb.com.vn/homes'
ip_website_url: str = 'https://nordvpn.com/what-is-my-ip/'


# ------------------------------------------------------------


cc_47NTB = r'https://www.airbnb.com.vn/s/Qu%E1%BA%ADn-1--H%E1%BB%93-Ch%C3%AD-Minh/homes?date_picker_type=flexible_dates&source=structured_search_input_header&search_type=user_map_move&monthly_start_date=2025-11-01&monthly_length=3&monthly_end_date=2026-02-01&price_filter_input_type=2&channel=EXPLORE&refinement_paths%5B%5D=%2Fhomes&price_filter_num_nights=2&place_id=ChIJe4jt-TgvdTERiYl2A1ftrRQ&acp_id=9d9f2413-8cc9-4792-b4b1-6bb1c8437794&flexible_trip_lengths%5B%5D=weekend_trip&query=Qu%E1%BA%ADn%201%2C%20H%E1%BB%93%20Ch%C3%AD%20Minh&search_mode=regular_search&ne_lat=10.770286888210231&ne_lng=106.70169632443458&sw_lat=10.768480627893807&sw_lng=106.70008758211003&zoom=19.297795796143774&zoom_level=19.297795796143774&search_by_map=true'

the_opera_q2 = 'https://www.airbnb.com.vn/s/The-Opera-Residence--Th%E1%BB%A7-%C4%90%E1%BB%A9c--Th%C3%A0nh-ph%E1%BB%91-H%E1%BB%93-Ch%C3%AD-Minh/homes?refinement_paths%5B%5D=%2Fhomes&acp_id=t-g-ChIJ2yDwGcgvdTERayL_S4sCgcQ&date_picker_type=flexible_dates&search_type=user_map_move&monthly_start_date=2025-12-01&monthly_length=3&monthly_end_date=2026-03-01&price_filter_input_type=2&channel=EXPLORE&zoom_level=19.150706754909642&price_filter_num_nights=2&place_id=ChIJ2yDwGcgvdTERayL_S4sCgcQ&flexible_trip_lengths%5B%5D=weekend_trip&query=The%20Opera%20Residence%2C%20Th%E1%BB%A7%20%C4%90%E1%BB%A9c%2C%20Th%C3%A0nh%20ph%E1%BB%91%20H%E1%BB%93%20Ch%C3%AD%20Minh&search_mode=regular_search&ne_lat=10.778257176409562&ne_lng=106.71308950700285&sw_lat=10.7766170606249&sw_lng=106.7117199228365&zoom=19.150706754909642&search_by_map=true'
the_metropole_q2 = ''
the_galleria_q2 = ''
the_empire_city_q2 = ''
the_river_q2 = ''


# scraping config ---------------------------------------------

log_error_level: LogErrorLevel = '3_level'

scrape_phase: int = 2

save_db: bool = False

test_local: bool = True

