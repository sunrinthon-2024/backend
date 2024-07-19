from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse
from interface.place import PlaceDetail, PlaceLocation, PlaceSleepType, Place
from database.place import Place as PlaceDatabase

from service.credential import depends_credential, Credential
from service.gmap import GmapClient

load_dotenv(verbose=True)
router = APIRouter(tags=["mapfind"], prefix="/mapfind")

match_place_types = {
    "hospital": "hospital",
    "subway_station": "subway_station",
    "school": "school",
    "doctor": "hospital",
}


@cbv(router)
class MapFind:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)
    gmap_client = GmapClient()

    @router.get("/scan", description="특정 위치 주변의 피난처,병원을 제공합니다.")
    async def scan(
        self, latitude: str, longitude: str, radius: int, max_results: int = 5
    ):
        places_data = await self.gmap_client.get_place_nearby(
            place_types=["hospital", "subway_station", "school", "doctor"],
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            max_results=max_results,
            field_mask=[
                "places.location",
                "places.displayName",
                "places.id",
                "places.primaryType",
                "places.types",
                "places.currentOpeningHours",
            ],
        )

        places = [
            Place(
                place_id=place_each["id"],
                display_name=place_each["displayName"]["text"],
                type=(
                    match_place_types[place_each.get("primaryType")]
                    if place_each.get("primaryType")
                    else match_place_types[place_each["types"][0]]
                ),
                location=PlaceLocation(
                    latitude=place_each["location"]["latitude"],
                    longitude=place_each["location"]["longitude"],
                ),
                open_now=(
                    place_each.get("currentOpeningHours").get("openNow")
                    if place_each.get("currentOpeningHours")
                    else False
                ),
            )
            for place_each in places_data["places"]
        ]

        return JSONResponse(
            code=200,
            message="Location updated successfully",
            data={"places": places},
        )

    @router.get(
        "/place/{place_id}",
        description="특정 플레이스의 정보를 제공합니다.",
    )
    async def place(self, place_id: str):
        if place_id.startswith("community:"):
            place_data = None
        else:
            place_data = await self.gmap_client.get_place_detail(place_id)

        place_database, _ = await PlaceDatabase.get_or_create(
            defaults={
                "place_id": place_data["id"],
                "display_name": place_data["displayName"]["text"],
            },
            place_id=place_id,
        )
        return JSONResponse(
            code=200,
            message="Location updated successfully",
            data=PlaceDetail(
                place_id=place_data["id"],
                display_name=place_data["displayName"]["text"],
                type=(
                    match_place_types[place_data.get("primaryType")]
                    if place_data.get("primaryType")
                    else match_place_types[place_data["types"][0]]
                ),
                phone_number=place_data["internationalPhoneNumber"],
                location=PlaceLocation(
                    latitude=place_data["location"]["latitude"],
                    longitude=place_data["location"]["longitude"],
                ),
                google_map_uri=place_data["googleMapsUri"],
                open_now=(
                    place_data.get("currentSecondaryOpeningHours")[0].get("openNow")
                    if place_data.get("currentSecondaryOpeningHours")
                    else False
                ),
                sleep_available=PlaceSleepType(place_database.sleep_available).value,
                safe_rating=place_database.safe_rating,
            ).model_dump(),
        )
