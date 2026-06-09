from pydantic import UUID4, BaseModel, Field


class CharacterCreateDTO(BaseModel):
    name: str = Field(max_length=128)
    description: str = Field(max_length=2048)
    prompt: str = Field(max_length=4096)

class CharacterCreateResponseDTO(BaseModel):
    character_id: UUID4