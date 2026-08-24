from pydantic import UUID4, BaseModel


class StartChatResponseDTO(BaseModel):
    chat_id: UUID4