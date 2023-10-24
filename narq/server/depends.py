from fastapi import Depends
from redis.asyncio.client import Redis
from starlette.requests import Request

from narq import Narq


def get_narq(request: Request) -> Narq:
    return request.app.narq


def get_redis(narq=Depends(get_narq)) -> Redis:
    return narq.redis


def get_pager(limit: int = 10, offset: int = 0):
    return limit, offset
