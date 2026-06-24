import asyncio

from fastapi import APIRouter, HTTPException, Query, Request, status
from loguru import logger
from pydantic import UUID4

from api.v1.schemas.base_dtos import CharacterDTO, UserDTO
from api.v1.schemas.frieren_hub_get import CharacterListResponseDTO
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
async def get_character_by_id(request: Request, character_id: UUID4):
    character = await Character.get_or_none(id=character_id).select_related('created_by')

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    likes = await request.app.state.redis_db.get_character_likes(character_id.id)

    return CharacterDTO(id=character.id,
                        name=character.name,
                        description=character.description,
                        model_url=character.model_url,
                        cover_url=character.cover_url,
                        likes=likes,
                        created_by=UserDTO(
                            id=character.created_by.id,
                            full_name=character.created_by.full_name
                        ))

@router.get('/all', response_model=CharacterListResponseDTO)
async def list_all_characters(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    characters, total = await asyncio.gather(
        Character.all().limit(limit).offset(offset).select_related('created_by'),
        Character.all().count()
    )

    try:
        return CharacterListResponseDTO(items=await serialize_characters_with_likes(characters=characters,
                                                                                    redis_client=request.app.state.redis),
                                         total=total)

    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')


@router.get('/all/{user_id}', response_model=CharacterListResponseDTO)
async def list_all_characters_from_user(
    request: Request,
    user_id: UUID4,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    characters, total = await asyncio.gather(
        Character.filter(created_by__id=user_id).limit(limit).offset(offset).select_related('created_by'),
        Character.filter(created_by__id=user_id).count()
    )

    try:
        return CharacterListResponseDTO(items=await serialize_characters_with_likes(characters=characters,
                                                                                    redis_client=request.app.state.redis), 
                                        total=total)
    
    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')