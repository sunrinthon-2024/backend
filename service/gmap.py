import os
from dotenv import load_dotenv

from utils.request import BaseRequest
from utils.string import create_url

load_dotenv(verbose=True)


class GmapClient(BaseRequest):
    async def get_location_info(self, latitude: str, longitude: str) -> dict:
        url = create_url(
            "https://maps.googleapis.com/maps/api/geocode/json?",
            latlng=f"{latitude},{longitude}",
            key=os.environ["GOOGLE_API_KEY"],
        )
        response = await self.get(url)
        return await response.json()

    async def get_place_nearby(
        self,
        place_types: list[str],
        latitude: str,
        longitude: str,
        radius: int,
        max_results: int,
        field_mask: list[str],
        extra_data: dict | None = None,
    ) -> dict:
        if extra_data is None:
            extra_data = {}
        url = "https://places.googleapis.com/v1/places:searchNearby"
        extra_data.update({
            "includedTypes": place_types,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude)
                    },
                    "radius": float(radius)
                }
            },
            "maxResultCount": max_results,
            "rankPreference": "DISTANCE",
        })
        print(extra_data)
        print(",".join(field_mask))
        response = await self.post(
            url,
            headers={
                "X-Goog-Api-Key": os.environ["GOOGLE_API_KEY"],
                "X-Goog-FieldMask": ",".join(field_mask),
            },
            json=extra_data,
        )
        return await response.json()
