from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from api.v1.deps.auth import get_current_user
from models.character import Character
from models.user import User

router = APIRouter()


@router.delete('/{character_id}')
async def delete_character(character_id: UUID4,
                           user: Annotated[User, Depends(get_current_user)]):
    character = await Character.get_or_none(id=character_id, created_by=user)

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    await character.delete()

    return {'status': 'ok'}