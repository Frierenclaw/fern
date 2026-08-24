from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import UUID4

from api.v1.deps.auth import get_current_user
from api.v1.deps.get_redis import get_redis
from core.clients import limiter
from models.character import Character
from models.user import User
from redis_db import Redis

router = APIRouter()


@router.delete('/{character_id}')
@limiter.limit('30/hour')
async def delete_character(request: Request,
                           character_id: UUID4,
                           user: Annotated[User, Depends(get_current_user)],
                           redis: Annotated[Redis, Depends(get_redis)]):
    character = await Character.get_or_none(id=character_id, created_by=user)

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    await character.delete()

    try:
        await redis.invalidate_character(character_id=character_id)
    except Exception as e:
        logger.exception(f'Error while trying to invalidate character from cache. Detail: {e}')

    return {'status': 'ok'}