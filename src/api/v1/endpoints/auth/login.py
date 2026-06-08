from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.auth_logic import Auth
from models.user import User

router = APIRouter()

DUMMY_HASH = bcrypt.hashpw(b'dummy_password', bcrypt.gensalt())

@router.post('/login')
async def login_endpoint(oauth: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Authenticate manager by email and password. Issues JWT tokens as HttpOnly cookies."""
    
    user = await User.get_or_none(email=oauth.username)

    if user:
        is_valid = await Auth.check_password(hashed_password=user.password,
                                       inputed_password=oauth.password)
    else:
        bcrypt.checkpw(oauth.password.encode('utf-8'), DUMMY_HASH)

        is_valid = False

    if not is_valid:
        raise HTTPException(
            detail='Wrong email or password',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = Auth.generate_access_token(user.id)
    refresh_token = Auth.generate_refresh_token(user.id)


    return {'status': 'ok',
            'access_token': access_token,
            'refresh_token': refresh_token}
