import os
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import redis.asyncio as redis

from app.redisconn import RedisConn

from fastapi import APIRouter, HTTPException, Depends, status, Request, Security
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from interface.response import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.bitflag import UserBitflag
from database.user import User as DatabaseUser
from service.google_oauth import GoogleOAuth

load_dotenv(verbose=True)
router = APIRouter(tags=["user"], prefix="/user")


async def get_redis_pool() -> redis.Redis:
    redis_pool = RedisConn(
        host=os.environ["REDIS_HOST"], port=int(os.environ["REDIS_PORT"]), db=0
    )
    return redis_pool.connection

security = HTTPBearer(
    scheme_name="User Access Token",
    description="/auth에서 발급받은 토큰을 입력해주세요",
)


@cbv(router)
class User:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    redis_pool: redis.Redis = Depends(get_redis_pool)

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.password_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return cls.password_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_token = jwt.encode(
            to_encode, os.environ["JWT_SECRET_KEY"], algorithm="HS256"
        )
        return encoded_token

    @staticmethod
    async def register_token(
        redis_pool: redis.Redis, expire: timedelta, user_id: str, token: str
    ):
        await redis_pool.hset("user", token, user_id)
        await redis_pool.expire(token, expire)

    @staticmethod
    async def delete_token(redis_pool: redis.Redis, token: str):
        await redis_pool.hdel("user", token)

    @staticmethod
    async def is_valid_token(redis_pool: redis.Redis, token: str):
        return await redis_pool.hexists("user", token)

    @staticmethod
    async def get_current_user(authorization: HTTPAuthorizationCredentials = Security(security)) -> DatabaseUser:
        session_token = authorization.credentials
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                session_token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception
        if not await User.is_valid_token(redis_pool=await get_redis_pool(), token=session_token):
            raise credentials_exception
        user = await DatabaseUser.get(id=user_id)
        if user is None:
            raise credentials_exception
        return user

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
        access_token = self.create_access_token(
            data={"sub": str(database_user.id)}, expires_delta=access_token_expires
        )
        try:
            await self.register_token(
                redis_pool=self.redis_pool,
                expire=access_token_expires,
                token=access_token,
                user_id=str(database_user.id),
            )
            token_expired_time = datetime.now() + access_token_expires
            return JSONResponse(
                code=200,
                message="Login successful",
                data={
                    "token": access_token,
                    "expired": int(token_expired_time.timestamp()),
                },
            )
        except Exception as _e:
            raise HTTPException(
                status_code=500, detail="Internal Server Error, " + str(_e)
            )

    @router.post("/logout", description="로그아웃하기 (토큰 만료시키기)")
    async def logout(
        self,
        request: Request,
        current_user: "DatabaseUser" = Depends(get_current_user),
    ):
        _current_user = await current_user
        token = request.headers["Authorization"].split(" ")[1]
        await self.delete_token(redis_pool=self.redis_pool, token=token)
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
