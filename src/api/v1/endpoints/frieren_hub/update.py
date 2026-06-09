from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.deps.auth import get_current_user
from api.v1.schemas.frieren_hub_update import CharacterUpdateDTO, CharacterUpdateResponseDTO
from models.character import Character
from models.user import User

router = APIRouter()

@router.patch('/character', response_model=CharacterUpdateResponseDTO)
async def update_character(dto: CharacterUpdateDTO,
                           user: Annotated[User, Depends(get_current_user)]):
    character = await Character.get_or_none(id=dto.character_id,
                                            created_by=user)
    
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    character.update_from_dict(dto.model_dump(exclude={'character_id'}, exclude_none=True))
    await character.save()

    return CharacterUpdateResponseDTO(character_id=character.id)