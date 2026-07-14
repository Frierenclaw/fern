from typing import Any, Literal

from pydantic import UUID4, BaseModel, ConfigDict, Field


class UserDTO(BaseModel):
    id: UUID4
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class CharacterDTO(BaseModel):
    id: UUID4
    name: str
    description: str
    cover_url: str | None
    model_url: str | None
    animations_url: str | None
    
    likes: int | None = None
    
    created_by: UserDTO

    model_config = ConfigDict(from_attributes=True)

class ClientFunctionInputSchemaProperty(BaseModel):
    type: Literal['string', 'number', 'integer', 'boolean', 'array', 'object']
    enum: list[str] | None = None
    description: str | None = None
    items: dict[str, Any] | None = None 


class ClientFunctionInputSchema(BaseModel):
    type: Literal['object'] = 'object'
    properties: dict[str, ClientFunctionInputSchemaProperty]
    required: list[str] = Field(default_factory=list)


class ClientFunctionDTO(BaseModel):
    name: str = Field(max_length=128)
    description: str

    input_schema: ClientFunctionInputSchema

class ClientDTO(BaseModel):
    id: UUID4
    
    app_version: str | None = Field(max_length=64)


    