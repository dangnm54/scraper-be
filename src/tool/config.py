import random

from src.type.data import BrowserMode, SearchMode, LogErrorLevel


# -----------------------------------------------------------------------------------


# wait time: 2 - 4s
wait_time: float = random.uniform(1, 2) + random.uniform(1, 2) - random.uniform(0.1, 0.5)


# website links
main_website_url: str = 'https://www.airbnb.com.vn/homes'
ip_website_url: str = 'https://nordvpn.com/what-is-my-ip/'

# main_website_url: str = r'https://www.airbnb.com.vn/s/homes?refinement_paths%5B%5D=%2Fhomes&location_search=NEARBY&date_picker_type=flexible_dates&source=structured_search_input_header&search_type=user_map_move&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2025-11-01&monthly_length=3&monthly_end_date=2026-02-01&search_mode=regular_search&price_filter_input_type=2&channel=EXPLORE&ne_lat=10.774215000859034&ne_lng=106.70149235310811&sw_lat=10.764020898917371&sw_lng=106.69241300354992&zoom=16.801140114402802&zoom_level=16.801140114402802&search_by_map=true&price_filter_num_nights=5'






# scraping config ---------------------------------------------


save_db: bool = False

search_mode: SearchMode = 'apply'

log_error_level: LogErrorLevel = '3_level'

scrape_phase: int = 2

test_local: bool = True

