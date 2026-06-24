from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import UUID4

from api.v1.deps.auth import get_current_user
from models.user import User

router = APIRouter()

@router.post('/like/{character_id}')
async def like_character(request: Request,
                         character_id: UUID4,
                         user: Annotated[User, Depends(get_current_user)]):
    try:
        await request.app.state.redis_db.like_character(character_id=character_id,
                                user_id=user.id)
    except Exception as e:
        logger.exception(e)

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Cannot like character. Please try again')
    
    return {'status': 'ok'}


@router.post('/unlike/{character_id}')
async def unlike_character(request: Request,
                           character_id: UUID4,
                           user: Annotated[User, Depends(get_current_user)]):
    try:
        await request.app.state.redis_db.unlike_character(character_id=character_id,
                                user_id=user.id)
    except Exception as e:
        logger.exception(e)

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Cannot unlike character. Please try again')
    
    return {'status': 'ok'}
