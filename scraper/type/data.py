from typing import Literal,Optional, List
from pydantic import BaseModel



ScrapeResult = Literal['Success', 'Failed', 'Partial']


class PropertyDetail(BaseModel):

    # overview_data 
    ID: str
    Scrape_result: ScrapeResult
    Guest_num: Optional[int] = None
    Bed_num: Optional[int] = None
    Bath_num: Optional[int] = None
    Location: Optional[str] = None


    # rating_data
    Rating_title: Optional[str] = None
    Rating_num: Optional[int] = None
    Rating_star: Optional[float] = None


    # host_data 
    Host_name: Optional[str] = None
    Host_title: Optional[str] = None
    Host_rating_star: Optional[float] = None
    Host_rating_num: Optional[int] = None
    Host_exp: Optional[str] = None
    Host_link: Optional[str] = None


    # booking_rate_data 
    This_month_booked_rate: Optional[float] = None
    Next_1_month_booked_rate: Optional[float] = None
    Next_3_month_booked_rate: Optional[float] = None


    # deffered -------------------------------------------------------
    # ___utility_data___
        # Utility_num: Optional[int] = None,
        # Utility_bathroom: Optional[int] = None
        # Utility_bedroom: Optional[List[str]] = None
        # Utility_entertain: Optional[List[str]] = None
        # Utility_safety: Optional[List[str]] = None
        # Utility_kitchen: Optional[List[str]] = None
        # Utility_outdoor: Optional[List[str]] = None
        # Utility_parking: Optional[List[str]] = None
        # Utility_service: Optional[List[str]] = None
        # Utility_not_included: Optional[List[str]] = None

    # ___rating_data___
        # Rating_clean_score: Optional[float] = None
        # Rating_accuracy_score: Optional[float] = None
        # Rating_checkin_score: Optional[float] = None
        # Rating_commu_score: Optional[float] = None
        # Rating_location_score: Optional[float] = None
        # Rating_value_score: Optional[float] = None

    # ___co-host_data___
        # Co_host_num: Optional[int] = None
        # Co_host_name: Optional[List[str]] = None
        # Co_host_link: Optional[List[str]] = None

    # ___booking_rate_data___
        # Last_1_month_booked_rate: Optional[float] = None
        # Last_3_month_booked_rate: Optional[float] = None    






