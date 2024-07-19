from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse

from service.credential import depends_credential, Credential

load_dotenv(verbose=True)
router = APIRouter(tags=["mapfind"], prefix="/mapfind")


@cbv(router)
class MapFind:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)

    ...
