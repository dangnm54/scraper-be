import random

from src.type.data import BrowserMode, SearchMode, LogErrorLevel


# -----------------------------------------------------------------------------------


# wait time: 2.5 - 5.5s
wait_time: float = random.uniform(1, 3) + random.uniform(2, 5) - random.uniform(0.1, 0.5)


# website links
main_website_url: str = 'https://www.airbnb.com.vn/homes'
ip_website_url: str = 'https://nordvpn.com/what-is-my-ip/'



# scraping config

save_db: bool = False

search_mode: SearchMode = 'none'

browser_mode: BrowserMode = 'headless'

log_error_level: LogErrorLevel = '3_level'

scrape_phase: int = 2

