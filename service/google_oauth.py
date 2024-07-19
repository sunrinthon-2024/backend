import os
import aiohttp
from dotenv import load_dotenv

load_dotenv(verbose=True)


class GoogleOAuth:
    @staticmethod
    async def get_access_token(code: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.googleapis.com/oauth2/v4/token",
                data={
                    "client_id": os.environ["GOOGLE_CLIENT_ID"],
                    "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
                },
            ) as response:
                data = await response.json()
                return data["access_token"]

    @staticmethod
    async def get_user(access_token: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as response:
                return await response.json()
