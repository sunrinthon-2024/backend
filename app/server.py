import os
import uvicorn
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from tortoise.contrib.fastapi import RegisterTortoise

from router import user, home, mapfind, raid
from utils.string import create_url

load_dotenv(verbose=True)
logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(server: FastAPI):
    print(
        create_url(
            "https://accounts.google.com/o/oauth2/v2/auth?",
            scope="email profile",
            state="security_token",
            redirect_uri=os.environ["GOOGLE_REDIRECT_URI"],
            response_type="code",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            access_type="online",
        )
    )
    async with RegisterTortoise(
        server,
        db_url=os.environ["DATABASE_URI"],
        modules={"models": [
            "database.user",
            "database.place",
        ]},
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        yield


app = FastAPI(
    lifespan=lifespan,
    title="Sunrinthon",
    description="솦과인내 어쩌구 팀",
    version="0.1",
)

app.include_router(user.router)
app.include_router(home.router)
app.include_router(mapfind.router)
app.include_router(raid.router)


@app.get("/")
async def root():
    return {"message": "Hello Sunrinthon"}


uvicorn.run(app, host="0.0.0.0", port=9001)
