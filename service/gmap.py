import os
from dotenv import load_dotenv

from utils.request import BaseRequest
from utils.string import create_url

load_dotenv(verbose=True)


class GmapClient(BaseRequest):
    async def get_location_info(self, latitude: str, longitude: str) -> dict:
        url = create_url(
            "https://maps.googleapis.com/maps/api/geocode/json",
            latlng=f"{latitude},{longitude}",
            key=os.environ["GOOGLE_API_KEY"],
        )
        response = await self.get(url)
        return await response.json()
