from dotenv import load_dotenv
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse
from interface.raid import RaidAlarm, RaidReport
from utils.string import get_name_from, transform_raid_data

from service.credential import depends_credential, Credential
from service.gmap import GmapClient
from service.uasiren import UASiren
from database.raid import RaidReport as RaidReportDatabase

load_dotenv(verbose=True)
router = APIRouter(tags=["raid"], prefix="/raid")


@cbv(router)
class Raid:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)
    gmap_client = GmapClient()
    uasiren = UASiren()

    @router.get("/scan", description="특정 위치 주변의 경보 가져오기")
    async def scan(self, latitude: str, longitude: str, max_results: int = 3):
        location_data = await self.gmap_client.get_location_info(latitude, longitude)
        area_level_name = get_name_from(
            location_data["results"], "administrative_area_level_1"
        )
        area_ua_name = self.uasiren.region_translate_ua(area_level_name)
        region_id = self.uasiren.get_region_id(area_ua_name)
        data: list[dict] = await self.uasiren.get_alerts(region_id)
        data.reverse()

        raid_report_list = await RaidReportDatabase.filter(
            area_level_name=area_level_name
        )
        return_data = [
            RaidAlarm(
                raid_id=each.raid_id,
                alert_type=each.alert_type,
                start_time=each.start_time,
                end_time=None,
                duration=None,
                is_continue=True,
            ).model_dump()
            for each in raid_report_list
        ]

        for each_raw in data:
            each = transform_raid_data(each_raw)
            return_data.append(
                RaidAlarm(
                    raid_id=each["id"],
                    alert_type=each["alertType"],
                    start_time=each["startDate"],
                    end_time=each["endDate"],
                    duration=each["duration"],
                    is_continue=each["isContinue"],
                ).model_dump()
            )

        set_return_data = return_data
        if len(return_data) > max_results:
            set_return_data = return_data[:max_results]

        raid_location = await self.gmap_client.get_location_from(area_level_name)
        results = raid_location.get("results", [])
        raid_location_geometry = None
        if results:
            raid_location_geometry = results[0]["geometry"]["location"]

        return JSONResponse(
            code=200,
            message="Success",
            data={
                "alerts": set_return_data,
                "region": area_level_name,
                "latitude": str(raid_location_geometry.get("lat") if results else ""),
                "longitude": str(raid_location_geometry.get("lng") if results else ""),
            },
        )

    @router.post("/report", description="미등록 상황 등록")
    async def report_raid(self, report_data: RaidReport):
        location_data = await self.gmap_client.get_location_info(
            str(report_data.location.latitude), str(report_data.location.longitude)
        )
        area_level_name = get_name_from(
            location_data["results"], "administrative_area_level_1"
        )
        create_result = await RaidReportDatabase.create(
            latitude=report_data.location.latitude,
            longitude=report_data.location.longitude,
            area_level_name=area_level_name,
            alert_type=report_data.alert_type,
            start_time=datetime.fromtimestamp(report_data.start_time),
            comment=report_data.comment,
        )

        return JSONResponse(
            code=200,
            message="Success",
            data={
                "report_id": create_result.raid_id,
            },
        )
