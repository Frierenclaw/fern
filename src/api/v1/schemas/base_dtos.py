from pydantic import UUID4, BaseModel, ConfigDict


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
    likes: int | None = None
    
    created_by: UserDTO

    model_config = ConfigDict(from_attributes=True)