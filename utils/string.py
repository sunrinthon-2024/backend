import math
from datetime import datetime
from urllib.parse import urlencode


def create_url(url: str, **kwargs) -> str:
    return url + urlencode(kwargs)


def get_country_locality_string(address_components: dict):
    content = address_components["plus_code"]["compound_code"]
    parts = content.split(",")
    return ",".join(parts[1:]).strip()


def get_name_from(data: list[dict], name_type: str) -> str:
    for item in data[0]["address_components"]:
        if name_type in item["types"]:
            return item["long_name"]


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


def transform_raid_data(alert_data: dict) -> dict:
    # duration을 초로 변환
    duration_parts = alert_data["duration"].split(":")
    hours = int(duration_parts[0])
    minutes = int(duration_parts[1])
    seconds = int(duration_parts[2])
    total_seconds = hours * 3600 + minutes * 60 + seconds
    alert_data["duration"] = total_seconds

    end_date = datetime.strptime(alert_data["endDate"], "%Y-%m-%dT%H:%M:%SZ")
    start_date = datetime.strptime(alert_data["startDate"], "%Y-%m-%dT%H:%M:%SZ")
    alert_data["endDate"] = end_date
    alert_data["startDate"] = start_date

    return alert_data
