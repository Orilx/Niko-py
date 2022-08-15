import os
from pathlib import Path
from random import choice

import nonebot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from nonebot.drivers.fastapi import Driver, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# https://slowapi.readthedocs.io/en/latest
limiter = Limiter(key_func=get_remote_address)

driver: Driver = nonebot.get_driver()
app: FastAPI = nonebot.get_app()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 设置允许跨域
origins = [
    "https://api.orilx.top/",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"Hello world"}


CAT_PATH = 'resources/images/cat/'


@app.get("/pic/cat")
@limiter.limit("5/second")
async def main(request: Request):
    return FileResponse(Path(CAT_PATH + choice(os.listdir(CAT_PATH))).absolute())


SETU_PATH = 'resources/images/setu/'


@app.get("/pic/setu")
@limiter.limit("5/second")
async def main(request: Request):
    return FileResponse(Path(SETU_PATH + choice(os.listdir(SETU_PATH))).absolute())
