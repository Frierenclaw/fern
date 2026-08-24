from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums.message_role import MessageRoleEnum


class ChatMessageDTO(BaseModel):
    role: MessageRoleEnum
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessagesResponseDTO(BaseModel):
    items: list[ChatMessageDTO]
