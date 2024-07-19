import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from interface.response import JSONResponse
import traceback

from app.bitflag import UserBitflag
from database.user import User as DatabaseUser
from service.google_oauth import GoogleOAuth
from service.credential import depends_credential, Credential, get_current_user
from service.session import Session, get_active_session

load_dotenv(verbose=True)
router = APIRouter(tags=["user"], prefix="/user")


@cbv(router)
class User:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    credential: Credential = Depends(depends_credential)

    @router.post(
        "/auth", description="토큰 생성 (회원가입 여부 상관없음, 자동 회원가입)"
    )
    async def register(self, code: str):
        try:
            token = await GoogleOAuth.get_access_token(code)
        except Exception as _:
            raise HTTPException(status_code=400, detail="Invalid code")
        google_user_data = await GoogleOAuth.get_user(token)
        if not await DatabaseUser.exists(email=google_user_data["email"]):
            new_user_id = uuid.uuid4()
            while await DatabaseUser.exists(id=str(uuid.uuid4())):
                new_user_id = uuid.uuid4()

            database_user = await DatabaseUser.create(
                id=new_user_id,
                username=google_user_data["name"],
                email=google_user_data["email"],
                profile_url=google_user_data["picture"],
                flags=UserBitflag(default=0).zip(),
            )
        else:
            database_user = await DatabaseUser.get(email=google_user_data["email"])

        access_token_expires = timedelta(days=10)
        access_token = self.credential.create_access_token(
            data={"sub": str(database_user.id)}, expires_delta=access_token_expires
        )
        try:
            await self.credential.register_token(
                expire=access_token_expires,
                token=access_token,
                user_id=str(database_user.id),
            )
            token_expired_time = datetime.now() + access_token_expires
            session = Session(token=access_token)
            await session.set_expire(access_token_expires)
            await session.update({})

            return JSONResponse(
                code=200,
                message="Login successful",
                data={
                    "token": access_token,
                    "expired": int(token_expired_time.timestamp()),
                },
            )
        except Exception as e:
            traceback.print_exception(e)
            raise HTTPException(
                status_code=500, detail="Internal Server Error, " + str(e)
            )

    @router.post("/logout", description="로그아웃하기 (토큰 만료시키기)")
    async def logout(
        self,
        request: Request,
        current_user: "DatabaseUser" = Depends(get_current_user),
    ):
        _current_user = await current_user
        token = request.headers["Authorization"].split(" ")[1]
        await self.credential.delete_token(token=token)
        return JSONResponse(code=200, message="Logout successful", data=None)

    @router.get("/@me", description="프로필 조회")
    async def get_profile(
        self,
        current_user: "DatabaseUser" = Depends(get_current_user),
    ):
        _current_user = await current_user
        return JSONResponse(
            code=200,
            message="Profile found",
            data={
                "username": _current_user.username,
                "email": _current_user.email,
                "profile_url": _current_user.profile_url,
            },
        )
