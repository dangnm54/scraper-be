from pydantic import BaseModel


# ------------------------------------------------------------------------------------------------


class HostDetail(BaseModel):
    name: str
    link: str

    title: str | None
    rating_num: int | None
    rating_star: float | None
    exp_time: str | None

    prop_num: int | None
    avg_prop_rv_num: float | None
    avg_prop_rv_star: float | None


