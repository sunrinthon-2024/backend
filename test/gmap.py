import requests


def search_nearby_places(api_key, location, radius, place_type):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": radius,
        "type": place_type,
        "key": api_key,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# API 키를 여기에 입력하세요.
api_key = "AIzaSyB3_8bYOreK3JPMZtF0P-RjtkiFSL1q-r4"

# 검색할 위치 (위도, 경도)
location = "37.7749,-122.4194"  # 예: 샌프란시스코

# 검색 반경 (미터 단위)
radius = 1500

# 검색할 장소 유형 (예: 'restaurant', 'cafe', 'hospital' 등)
place_type = "restaurant"

places = search_nearby_places(api_key, location, radius, place_type)

if places:
    for place in places["results"]:
        print(f"Name: {place['name']}, Address: {place['vicinity']}")
else:
    print("Failed to fetch places")
