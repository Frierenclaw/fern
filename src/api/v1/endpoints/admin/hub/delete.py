from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from api.v1.deps.auth import admin_rights_required
from models.character import Character
from models.user import User

router = APIRouter()


@router.delete('/{character_id}')
async def delete_character(character_id: UUID4,
                           admin: Annotated[User, Depends(admin_rights_required)]):
    character = await Character.get_or_none(id=character_id)

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    await character.delete()

    return {'status': 'ok'}