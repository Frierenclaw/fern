from pydantic import BaseModel, Field

from core.config import config


class CreateCompletionRequestDTO(BaseModel):
    """
    Only the new user message: the history is kept server-side,
    see api.v1.chat_logic.layer.ChatLayer
    """

    message: str = Field(min_length=1, max_length=config.CHAT_MAX_MESSAGE_LENGTH)

    model: str | None = None # Defaults to config.HEITER_MODEL_NAME
    max_tokens: int | None = Field(default=None, ge=1)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)

    stream: bool = True
