import os
import uvicorn
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from tortoise.contrib.fastapi import RegisterTortoise

load_dotenv(verbose=True)
logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(server: FastAPI):
    async with RegisterTortoise(
        server,
        db_url=os.environ["DATABASE_URI"],
        modules={"models": []},
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


@app.get("/")
async def root():
    return {"message": "Hello Sunrinthon"}


uvicorn.run(app, host="0.0.0.0", port=8000)