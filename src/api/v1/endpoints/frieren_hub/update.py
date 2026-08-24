from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger

from api.v1.deps.auth import get_current_user
from api.v1.deps.get_redis import get_redis
from api.v1.schemas.frieren_hub_update import CharacterUpdateDTO, CharacterUpdateResponseDTO
from core.clients import limiter
from models.character import Character
from models.user import User
from redis_db import Redis

router = APIRouter()

@router.patch('/character', response_model=CharacterUpdateResponseDTO)
@limiter.limit('60/hour')
async def update_character(request: Request,
                           dto: CharacterUpdateDTO,
                           user: Annotated[User, Depends(get_current_user)],
                           redis: Annotated[Redis, Depends(get_redis)]):
    character = await Character.get_or_none(id=dto.character_id,
                                            created_by=user)
    
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    character.update_from_dict(dto.model_dump(exclude={'character_id'}, exclude_none=True))
    await character.save()

    try:
        await redis.invalidate_character(character_id=dto.character_id)
    except Exception as e:
        logger.exception(f'Error while trying to invalidate character from cache. Detail: {e}')
        
    return CharacterUpdateResponseDTO(character_id=character.id)