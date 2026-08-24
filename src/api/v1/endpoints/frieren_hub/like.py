from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import UUID4

from api.v1.deps.auth import get_current_user
from api.v1.deps.get_redis import get_redis
from core.clients import limiter
from models.user import User
from redis_db import Redis

router = APIRouter()

@router.post('/like/{character_id}')
@limiter.limit('30/minute;300/hour')
async def like_character(request: Request,
                         character_id: UUID4,
                         redis: Annotated[Redis, Depends(get_redis)],
                         user: Annotated[User, Depends(get_current_user)]):
    try:
        await redis.like_character(character_id=character_id,
                                user_id=user.id)
    except Exception as e:
        logger.exception(e)

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Cannot like character. Please try again')
    
    return {'status': 'ok'}


@router.post('/unlike/{character_id}')
@limiter.limit('30/minute;300/hour')
async def unlike_character(request: Request,
                           character_id: UUID4,
                           user: Annotated[User, Depends(get_current_user)],
                           redis: Annotated[Redis, Depends(get_redis)]):
    try:
        await redis.unlike_character(character_id=character_id,
                                user_id=user.id)
    except Exception as e:
        logger.exception(e)

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Cannot unlike character. Please try again')
    
    return {'status': 'ok'}
