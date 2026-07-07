from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import UUID4
from tortoise.transactions import in_transaction

from api.v1.deps.auth import admin_rights_required
from api.v1.schemas.admin_update_user import UpdateUserRequestDTO
from models.user import User

router = APIRouter()

@router.patch('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def edit_user(admin: Annotated[User, Depends(admin_rights_required)],
                    user_id: UUID4,
                    dto: UpdateUserRequestDTO):
    async with in_transaction() as con:
        user = await User.filter(id=user_id).select_for_update().using_db(con).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='User not found')
        
        try:
            await user.update_from_dict(dto.model_dump(exclude_none=True))
            await user.save()
        except Exception as e:
            logger.exception(f'Error while trying to update user. Detail: {e}')

            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail='Cannot update user. Please try again')
        
