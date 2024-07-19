import redis

from service.credential import get_redis_pool
from datetime import timedelta

from fastapi import HTTPException, status, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(
    scheme_name="User Access Token",
    description="/auth에서 발급받은 토큰을 입력해주세요",
)


class Session:
    def __init__(self, token: str):
        self.token = token
        self.redis_connection = get_redis_pool()

    async def set_expire(self, expire: timedelta) -> None:
        session_key = "TokenSession" + self.token
        await self.redis_connection.expire(session_key, expire)

    async def update(self, data: dict) -> None:
        session_key = "TokenSession" + self.token
        await self.redis_connection.hset("session", session_key, data)

    async def delete(self) -> None:
        session_key = "TokenSession" + self.token
        await self.redis_connection.hdel("session", session_key)

    @staticmethod
    async def is_valid(redis_pool: redis.Redis, token: str) -> bool:
        session_key = "TokenSession" + token
        return await redis_pool.hexists("session", session_key)


async def get_active_session(
    authorization: HTTPAuthorizationCredentials = Security(security),
) -> Session:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if await Session.is_valid(token=authorization.credentials):
        return Session(token=authorization.credentials)
    else:
        raise credentials_exception
