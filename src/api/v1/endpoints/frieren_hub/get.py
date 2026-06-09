import asyncio

from fastapi import APIRouter, HTTPException, Query, status
from loguru import logger
from pydantic import UUID4

from api.v1.schemas.base_dtos import CharacterDTO, UserDTO
from api.v1.schemas.frieren_hub_get import CharacterListResponseDTO
from models.character import Character

router = APIRouter()

@router.get('/character/{character_id}', response_model=CharacterDTO)
async def get_character_by_id(character_id: UUID4):
    character = await Character.get_or_none(id=character_id).select_related('created_by')

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    return CharacterDTO(id=character.id,
                        name=character.name,
                        description=character.description,
                        model_url=character.model_url,
                        cover_url=character.cover_url,
                        created_by=UserDTO(
                            id=character.created_by.id,
                            full_name=character.created_by.full_name
                        ))

@router.get('/all', response_model=CharacterListResponseDTO)
async def list_all_characters(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    characters, total = await asyncio.gather(
        Character.all().limit(limit).offset(offset).select_related('created_by'),
        Character.all().count()
    )

    serialized_characters = [CharacterDTO(
        id=character.id,
        name=character.name,
        description=character.description,
        cover_url=character.cover_url,
        model_url=character.model_url,
        created_by=UserDTO(
            id=character.created_by.id,
            full_name=character.created_by.full_name
        )
    ) for character in characters]

    try:
        return CharacterListResponseDTO(items=serialized_characters, total=total)
    
    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')


@router.get('/all/{user_id}', response_model=CharacterListResponseDTO)
async def list_all_characters_from_user(
    user_id: UUID4,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    characters, total = await asyncio.gather(
        Character.filter(created_by__id=user_id).limit(limit).offset(offset).select_related('created_by'),
        Character.filter(created_by__id=user_id).count()
    )

    serialized_characters = [CharacterDTO(
        id=character.id,
        name=character.name,
        description=character.description,
        cover_url=character.cover_url,
        model_url=character.model_url,
        created_by=UserDTO(
            id=character.created_by.id,
            full_name=character.created_by.full_name
        )
    ) for character in characters]

    try:
        return CharacterListResponseDTO(items=serialized_characters, total=total)
    
    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=503, detail='Error while serializing characters')