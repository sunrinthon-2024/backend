from typing import Literal
from pydantic import BaseModel


class RaidAlarm(BaseModel):
    raid_id: int
    alert_type: Literal["AIR", "URBAN_FIGHTS", "ARTILLERY"]
    start_time: str
    end_time: str
    duration: str
    is_continue: bool
