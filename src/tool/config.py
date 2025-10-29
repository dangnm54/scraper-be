import random

from src.type.data import BrowserMode, SearchMode, LogErrorLevel


# ------------------------------------------------------------


# wait time: 2 - 4s
wait_time: float = random.uniform(1, 2) + random.uniform(1, 2) - random.uniform(0.1, 0.5)


# website links
main_website_url: str = 'https://www.airbnb.com.vn/homes'
ip_website_url: str = 'https://nordvpn.com/what-is-my-ip/'


# ------------------------------------------------------------


cc_47NTB = r'https://www.airbnb.com.vn/s/Qu%E1%BA%ADn-1--H%E1%BB%93-Ch%C3%AD-Minh/homes?date_picker_type=flexible_dates&source=structured_search_input_header&search_type=user_map_move&monthly_start_date=2025-11-01&monthly_length=3&monthly_end_date=2026-02-01&price_filter_input_type=2&channel=EXPLORE&refinement_paths%5B%5D=%2Fhomes&price_filter_num_nights=2&place_id=ChIJe4jt-TgvdTERiYl2A1ftrRQ&acp_id=9d9f2413-8cc9-4792-b4b1-6bb1c8437794&flexible_trip_lengths%5B%5D=weekend_trip&query=Qu%E1%BA%ADn%201%2C%20H%E1%BB%93%20Ch%C3%AD%20Minh&search_mode=regular_search&ne_lat=10.770180276297397&ne_lng=106.70156029416819&sw_lat=10.768374104070984&sw_lng=106.69995163086992&zoom=19.29786666742596&zoom_level=19.29786666742596&search_by_map=true&disable_auto_translation=true'




# scraping config ---------------------------------------------

search_mode: SearchMode = 'apply'

log_error_level: LogErrorLevel = '3_level'

scrape_phase: int = 2

save_db: bool = True

test_local: bool = False

