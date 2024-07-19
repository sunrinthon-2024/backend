from typing import Literal
from pydantic import BaseModel

place_types = Literal["hospital", "school", "subway_station", "hospital", "community_shelter"]


class PlaceLocation(BaseModel):
    latitude: float
    longitude: float


class Place(BaseModel):
    place_id: str
    display_name: str
    type: place_types
    location: PlaceLocation
