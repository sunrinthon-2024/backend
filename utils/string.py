import math
from urllib.parse import urlencode


def create_url(url: str, **kwargs) -> str:
    return url + urlencode(kwargs)


def get_country_locality_string(address_components: dict):
    content = address_components["plus_code"]["compound_code"]
    parts = content.split(",")
    return ",".join(parts[1:]).strip()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    earthR = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earthR * c
    return distance
