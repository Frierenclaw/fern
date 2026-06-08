from fastapi import APIRouter, HTTPException, status
from loguru import logger

from api.v1.auth_logic import Auth
from api.v1.schemas.auth_register import RegisterDTO
from models.user import User

router = APIRouter()

@router.post('/register')
async def register(dto: RegisterDTO):
    user_exists = await User.filter(email=dto.email).exists()

    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='This email already registred')
    
    hashed_password = await Auth.hash_password(dto.password)

    try:
        await User.create(email=dto.email,
                          full_name=dto.full_name,
                          password=hashed_password)
    except Exception as e:
        logger.error(f'Error while trying to register user. Detail: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Cannot register user. Please try again in few minutes')
    
    return {'status': 'ok'}