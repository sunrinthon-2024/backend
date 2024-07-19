import requests


def get_coordinates(api_key, address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None, None
    else:
        return None, None


# 예시 데이터
api_key = "AIzaSyB3_8bYOreK3JPMZtF0P-RjtkiFSL1q-r4"
address = "Kyiv, Ukraine"

latitude, longitude = get_coordinates(api_key, address)

if latitude is not None and longitude is not None:
    print(
        f"The coordinates of {address} are: Latitude {latitude}, Longitude {longitude}"
    )
else:
    print("Failed to fetch coordinates")
