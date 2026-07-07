from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from api.v1.auth_logic import Auth
from api.v1.deps.auth import admin_rights_required
from api.v1.schemas.admin_create_user import AdminCreateUser
from models.user import User

router = APIRouter()

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(admin: Annotated[User, Depends(admin_rights_required)],
                      dto: AdminCreateUser):
    user_exists = await User.filter(email=dto.email).exists()

    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='User already exists')
    
    hashed_password = await Auth.hash_password(dto.password)

    try:
        await User.create(**dto.model_dump(exclude={'password'}),
                          password=hashed_password)
    except Exception as e:
        logger.exception(f'Error while trying to create user. Detail: {e}')
        
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Cannot to create user. Please try again in few minutes')
    
    return {'status': 'ok'}
