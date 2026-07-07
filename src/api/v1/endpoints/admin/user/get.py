import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from api.v1.deps.auth import admin_rights_required
from api.v1.schemas.admin_list_users import ListUsersResponseDTO
from api.v1.schemas.base_dtos import UserDTO
from models.user import User

router = APIRouter()

@router.get('/', response_model=ListUsersResponseDTO)
async def list_users(admin: Annotated[User, Depends(admin_rights_required)],
                     limit: int = Query(20, ge=1, le=100),
                     offset: int = Query(0, ge=0)):
    users, total = await asyncio.gather(
        User.filter().limit(limit).offset(offset),
        User.filter().count()
    )

    try:
        return ListUsersResponseDTO(items=[UserDTO.model_validate(user) for user in users], 
                                        total=total)
    except ValueError as e:
        logger.error(f'Error while serializing characters. Detail: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Error while serializing characters')
