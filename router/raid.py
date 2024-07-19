from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse
from interface.raid import RaidAlarm
from utils.string import get_name_from

from service.credential import depends_credential, Credential
from service.gmap import GmapClient
from service.uasiren import UASiren

load_dotenv(verbose=True)
router = APIRouter(tags=["raid"], prefix="/raid")


@cbv(router)
class Raid:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)
    gmap_client = GmapClient()
    uasiren = UASiren()

    @router.get("/scan", description="특정 위치 주변의 경보 가져오기")
    async def scan(
        self, latitude: str, longitude: str, max_results: int = 3
    ):
        location_data = await self.gmap_client.get_location_info(latitude, longitude)
        area_level_name = get_name_from(location_data["results"], "administrative_area_level_1")
        area_ua_name = self.uasiren.region_translate_ua(area_level_name)
        region_id = self.uasiren.get_region_id(area_ua_name)
        data: list[dict] = await self.uasiren.get_alerts(region_id)
        data.reverse()

        return_data = [RaidAlarm(
            raid_id=each["id"],
            alert_type=each["alertType"],
            start_time=each["startDate"],
            end_time=each["endDate"],
            duration=each["duration"],
            is_continue=each["isContinue"],
        ).model_dump() for each in data]

        set_return_data = return_data
        if len(return_data) > max_results:
            set_return_data = return_data[:max_results]

        raid_location = await self.gmap_client.get_location_from(area_level_name)
        results = raid_location.get('results', [])
        raid_location_geometry = None
        if results:
            raid_location_geometry = results[0]['geometry']['location']

        return JSONResponse(
            code=200,
            message="Success",
            data={
                "alerts": set_return_data,
                "region": area_level_name,
                "latitude": str(raid_location_geometry.get("lat") if results else ""),
                "longitude": str(raid_location_geometry.get("lng") if results else ""),
            }
        )




