from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse
from interface.session import Session as SessionInterface

from database.user import User as DatabaseUser
from service.credential import depends_credential, Credential, get_current_user
from service.session import Session, get_active_session
from service.gmap import GmapClient

from utils.string import get_country_locality_string

load_dotenv(verbose=True)
router = APIRouter(tags=["home"], prefix="/home")


@cbv(router)
class Home:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)
    gmap_client = GmapClient()

    @router.post("/location", description="사용자의 홈 화면 접속 시 위치를 전송하세요")
    async def update_location(
        self,
        latitude: str,
        longitude: str,
        current_user: "DatabaseUser" = Depends(get_current_user),
        session: "Session" = Depends(get_active_session),
    ):
        _current_user = await current_user

        await session.update(
            SessionInterface(
                location={
                    "latitude": latitude,
                    "longitude": longitude,
                }
            ).model_dump()
        )

        location_data = await self.gmap_client.get_location_info(latitude, longitude)
        location_string = get_country_locality_string(location_data)

        return JSONResponse(
            code=200,
            message="Location updated successfully",
            data={"location": location_string},
        )
