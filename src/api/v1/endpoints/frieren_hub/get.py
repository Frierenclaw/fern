from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from pydantic import UUID4
from redis.asyncio import Redis as RedisPure

from api.v1.deps.get_pure_redis import get_pure_redis
from api.v1.deps.get_redis import get_redis
from api.v1.schemas.base_dtos import CharacterDTO, UserDTO
from api.v1.schemas.frieren_hub_get import CharacterListResponseDTO
from core.clients import limiter
from models.character import Character
from redis_db import Redis

router = APIRouter()

async def serialize_characters_with_likes(characters: list[Character],
                                          redis_client: Redis) -> list[CharacterDTO]:
    async with redis_client.pipeline() as pipe:
        for character in characters:
            pipe.zcard(f"likes:character:{character.id}")
        likes_list = await pipe.execute()

    return [
        CharacterDTO(
            id=character.id,
            name=character.name,
            description=character.description,
            cover_url=character.cover_url,
            animations_url=character.animations_url,
            model_url=character.model_url,
            likes=likes,
            created_by=UserDTO(
                id=character.created_by.id,
                full_name=character.created_by.full_name
            )
        )
        for character, likes in zip(characters, likes_list, strict=True)
    ]

@router.get('/character/{character_id}', response_model=CharacterDTO)
@limiter.limit('60/minute')
async def get_character_by_id(request: Request, 
                              character_id: UUID4, 
                              redis: Annotated[Redis, Depends(get_redis)]):
    character = await Character.get_or_none(id=character_id).select_related('created_by')

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    likes = await redis.get_character_likes(character_id)

    return CharacterDTO(id=character.id,
                        name=character.name,
                        description=character.description,
                        model_url=character.model_url,
                        cover_url=character.cover_url,
                        animations_url=character.animations_url,
                        likes=likes,
                        created_by=UserDTO(
                            id=character.created_by.id,
                            full_name=character.created_by.full_name
                        ))

@router.get('/all', response_model=CharacterListResponseDTO)
@limiter.limit('30/minute')
async def list_all_characters(
    request: Request,
    redis: Annotated[RedisPure, Depends(get_pure_redis)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    characters = await Character.all().limit(limit).offset(offset).select_related('created_by')

    try:
        return CharacterListResponseDTO(items=await serialize_characters_with_likes(characters=characters,
                                                                                    redis_client=redis))

    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')


@router.get('/all/{user_id}', response_model=CharacterListResponseDTO)
@limiter.limit('30/minute')
async def list_all_characters_from_user(
    request: Request,
    user_id: UUID4,
    redis: Annotated[RedisPure, Depends(get_pure_redis)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    characters  = await Character.filter(created_by__id=user_id).limit(limit).offset(offset).select_related('created_by')
    try:
        return CharacterListResponseDTO(items=await serialize_characters_with_likes(characters=characters,
                                                                                    redis_client=redis))
    
    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')
