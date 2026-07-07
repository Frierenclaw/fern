from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from api.v1.auth_logic import Auth
from models.enums.role import RoleEnum
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

async def get_current_user(auth_token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        decode_result = Auth.decode_access_token(auth_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired',
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
        )
    
    user = await User.get_or_none(id=decode_result.get('user_id'))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found. Unauthorized.')
    
    return user

async def admin_rights_required(user: Annotated[User, Depends(get_current_user)]):
    if user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='No permissions')
    
    return user