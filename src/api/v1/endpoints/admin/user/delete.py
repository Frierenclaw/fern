from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import UUID4

from api.v1.deps.auth import admin_rights_required
from models.user import User

router = APIRouter()

@router.delete('/{user_id}')
async def delete_user(admin: Annotated[User, Depends(admin_rights_required)],
                      user_id: UUID4):
    user = await User.get_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    try:
        await user.delete()
    except Exception as e:
        logger.exception(f'Error while trying to delete user. Detail: {e}')

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Error while trying to delete user. Please try again in few minutes')
    
    return {'status': 'ok'}