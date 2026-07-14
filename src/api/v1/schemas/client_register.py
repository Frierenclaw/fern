from pydantic import BaseModel

from api.v1.schemas.base_dtos import ClientDTO, ClientFunctionDTO


class RegisterClientRequestDTO(BaseModel):
    client: ClientDTO
    functions: list[ClientFunctionDTO]