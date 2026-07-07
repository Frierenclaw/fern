from pydantic import BaseModel

from api.v1.schemas.base_dtos import UserDTO


class ListUsersResponseDTO(BaseModel):
    items: list[UserDTO]