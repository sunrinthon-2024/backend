from datetime import datetime, timedelta
from pydantic import BaseModel

from interface.place import PlaceLocation


class RaidAlarm(BaseModel):
    raid_id: int
    alert_type: str  # Literal["AIR", "URBAN_FIGHTS", "ARTILLERY"] 그러나 확실하지 않음.
    start_time: datetime | None
    end_time: datetime | None
    duration: int | None  # second
    is_continue: bool


class RaidReport(BaseModel):
    location: PlaceLocation
    alert_type: str
    start_time: int  # datetime
    comment: str  # 간략한 상황 설명
