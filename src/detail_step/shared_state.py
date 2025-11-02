"""
- this file only store cancel_status 
- use case: cancel scraping process from FE
- location of use
    - app.py: 
        - run_scraper_api
        - cancel_scraper_api
    - base.py: 
        - scrape_p2: for loop
        - run_full_flow
    - scrape_p1: view_page_get_all_link
"""

cancel_status: bool = False