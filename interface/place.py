from enum import Enum
from typing import Literal
from pydantic import BaseModel

place_types = Literal["hospital", "school", "subway_station"]


class PlaceSleepType(Enum):
    unavailable = 0
    available = 1
    unknown = -1


class PlaceLocation(BaseModel):
    latitude: float
    longitude: float


class Place(BaseModel):
    place_id: str
    display_name: str
    type: place_types
    open_now: bool
    location: PlaceLocation


class PlaceDetail(BaseModel):
    place_id: str
    display_name: str
    type: place_types
    phone_number: str
    location: PlaceLocation
    google_map_uri: str
    open_now: bool
    sleep_available: int
    safe_rating: int  # 1 ~ 5
