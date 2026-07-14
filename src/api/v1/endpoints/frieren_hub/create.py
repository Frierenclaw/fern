import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from loguru import logger
from pydantic import UUID4

from api.v1.deps.auth import get_current_user
from api.v1.s3 import S3Client
from api.v1.schemas.frieren_hub_create import CharacterCreateDTO, CharacterCreateResponseDTO
from core.config import config
from models.character import Character
from models.user import User

router = APIRouter()

@router.post('/', response_model=CharacterCreateResponseDTO)
async def create_new_character(dto: CharacterCreateDTO,
                               user: Annotated[User, Depends(get_current_user)]):
    try:
        character = await Character.create(
            **dto.model_dump(),
            created_by=user
        )
    except Exception as e:
        logger.error(f'Cannot create character. Detail: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Cannot create character. Please try again in few minutes')
    
    return CharacterCreateResponseDTO(character_id=character.id)


@router.post('/cover')
async def upload_cover(cover: UploadFile,
                       user: Annotated[User, Depends(get_current_user)],
                       character_id: UUID4):
    _, extension = os.path.splitext(cover.filename)
    
    if extension.lower() not in config.ALLOWED_COVER_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Allowed formats: {", ".join(config.ALLOWED_COVER_EXTENSIONS)}')
    
    if cover.content_type not in config.ALLOWED_COVER_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid content type')

    if cover.size and cover.size > config.MAX_COVER_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'Cover size must be less than {config.MAX_COVER_SIZE} bytes')

    character = await Character.get_or_none(id=character_id, created_by=user)
    
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    filename = f'{character.id}_cover{extension.lower()}'
    cover_io = await cover.read()

    s3 = S3Client()
    cover_url = await s3.upload_object(filename, cover_io, content_type=cover.content_type)
    
    character.cover_url = cover_url
    await character.save(update_fields=['cover_url'])

    return {'status': 'ok'}

@router.post('/model')
async def upload_model(model: UploadFile,
                       user: Annotated[User, Depends(get_current_user)],
                       character_id: UUID4):
    _, extension = os.path.splitext(model.filename)
    
    if extension.lower() not in config.ALLOWED_MODEL_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Allowed formats: {", ".join(config.ALLOWED_COVER_EXTENSIONS)}')
    
    if model.content_type not in config.ALLOWED_MODEL_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid content type')

    if model.size and model.size > config.MAX_MODEL_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'Model size must be less than {config.MAX_MODEL_SIZE} bytes')

    character = await Character.get_or_none(id=character_id, created_by=user)
    
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    filename = f'{character.id}_model{extension.lower()}'
    model_io = await model.read()

    s3 = S3Client()
    model_url = await s3.upload_object(filename, model_io, content_type=model.content_type)
    
    character.model_url = model_url
    await character.save(update_fields=['model_url'])

    return {'status': 'ok'}

@router.post('/animations')
async def upload_animations(animations: UploadFile,
                            user: Annotated[User, Depends(get_current_user)],
                            character_id: UUID4):  
    _, extension = os.path.splitext(animations.filename)
    
    if extension.lower() not in config.ALLOWED_ANIMATIONS_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Allowed formats: {", ".join(config.ALLOWED_ANIMATIONS_EXTENSIONS)}')
    
    if animations.content_type not in config.ALLOWED_ANIMATIONS_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid content type')

    if animations.size and animations.size > config.MAX_ANIMATIONS_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'Animations size must be less than {config.MAX_MODEL_SIZE} bytes')

    character = await Character.get_or_none(id=character_id, created_by=user)
    
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    filename = f'{character.id}_model{extension.lower()}'
    animations_io = await animations.read()

    s3 = S3Client()
    animations_url = await s3.upload_object(filename, animations_io, content_type=animations.content_type)
    
    character.animations_url = animations_url
    await character.save(update_fields=['animations_url'])

    return {'status': 'ok'}