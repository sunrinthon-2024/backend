from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse

from service.credential import depends_credential, Credential
from service.gmap import GmapClient

load_dotenv(verbose=True)
router = APIRouter(tags=["mapfind"], prefix="/mapfind")


@cbv(router)
class MapFind:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)
    gmap_client = GmapClient()

    @router.get("/scan", description="특정 위치 주변의 피난처,병원을 제공합니다.")
    async def scan(self, latitude: str, longitude: str, radius: int, max_results: int = 5):
        places = await self.gmap_client.get_place_nearby(
            place_types=["hospital", "subway_station", "school", "doctor"],
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            max_results=max_results,
            field_mask=["places.location", "places.displayName", "places.id", "places.primaryType", "places.types", "places.currentOpeningHours"]
        )

        return JSONResponse(
            code=200,
            message="Location updated successfully",
            data=places,
        )
