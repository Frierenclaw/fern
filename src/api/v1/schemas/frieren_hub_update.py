from pydantic import UUID4, BaseModel, Field


class CharacterUpdateDTO(BaseModel):
    character_id: UUID4
    
    name: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=2048)
    prompt: str | None = Field(default=None, max_length=4096)

class CharacterUpdateResponseDTO(BaseModel):
    character_id: UUID4