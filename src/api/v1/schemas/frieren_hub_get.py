from pydantic import BaseModel

from api.v1.schemas.base_dtos import CharacterDTO


class CharacterListResponseDTO(BaseModel):
    items: list[CharacterDTO]

    total: int