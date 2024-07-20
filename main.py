from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from starlette.requests import Request
from redis import asyncio as aioredis

from contextlib import asynccontextmanager

from typing import Annotated
from dotenv import load_dotenv
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis = await aioredis.Redis.from_url(redis_url)
        await FastAPILimiter.init(redis)

        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    

app = FastAPI(lifespan=lifespan)

def rate_limit_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=429,
        content={"message": "You've reached the rate limit!"}
    )

def rate_limit_header(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=429,
        content={"message": "You've reached the rate limit!"},
        headers={"X-RateLimit-Limit": "5"}
    )
app.add_exception_handler(HTTPException, rate_limit_exception_handler)
app.add_exception_handler(HTTPException, rate_limit_header)
app.mount("/static", StaticFiles(directory="static"), name="static")

MaxRateLimitDependency=Annotated[RateLimiter, Depends(RateLimiter(times=5, minutes=1))]
RateLimit3Dependency=Annotated[RateLimiter, Depends(RateLimiter(times=3, minutes=1))]

app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("static/fastapi.svg")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root(request: Request, rate_limiter: MaxRateLimitDependency):
    return {"message": "Welcome to the rate-limited FastAPI app!"}

@app.get("/limited")
async def limited(request: Request, rate_limiter: RateLimit3Dependency):
    return {"message": "This endpoint is limited to 3 requests per minute."}

@app.get("/open")
async def open_endpoint():
    return {"message": "This endpoint is not rate-limited."}
