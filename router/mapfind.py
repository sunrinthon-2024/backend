import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext

from interface.response import JSONResponse
from fastapi.security import HTTPBearer

from app.bitflag import UserBitflag
from database.user import User as DatabaseUser
from service.google_oauth import GoogleOAuth
from service.credential import depends_credential, Credential, get_current_user

load_dotenv(verbose=True)
router = APIRouter(tags=["mapfind"], prefix="/mapfind")


security = HTTPBearer(
    scheme_name="User Access Token",
    description="/auth에서 발급받은 토큰을 입력해주세요",
)


@cbv(router)
class MapFind:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)

    ...
