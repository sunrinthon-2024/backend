import requests
import json


def get_location_info(latitude, longitude, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]
        else:
            return None
    else:
        return None


latitude = 50.44717
longitude = 30.52412

api_key = "AIzaSyB3_8bYOreK3JPMZtF0P-RjtkiFSL1q-r4"

location_info = get_location_info(latitude, longitude, api_key)
if location_info:
    print(json.dumps(location_info, indent=2))
else:
    print("지역 정보를 가져오는 데 실패했습니다.")
