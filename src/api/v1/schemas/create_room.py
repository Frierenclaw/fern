from pydantic import UUID4, BaseModel


class CreateRoomDTO(BaseModel):
    character_id: UUID4
    wake_words: list[str]

    client_id: UUID4 | None = None
    animations: list[str] | None = None