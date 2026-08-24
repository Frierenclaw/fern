from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import UUID4

from api.v1.chat_logic import ChatLayer
from api.v1.deps.auth import get_current_user
from api.v1.deps.get_chat_layer import get_chat_layer
from api.v1.schemas.chat_get_messages import ChatMessageDTO, ChatMessagesResponseDTO
from core.clients import limiter
from models.chat import Message
from models.user import User

router = APIRouter()

@router.get('/{chat_id}/messages', response_model=ChatMessagesResponseDTO)
@limiter.limit('60/minute')
async def get_chat_messages(request: Request,
                            chat_id: UUID4,
                            user: Annotated[User, Depends(get_current_user)],
                            chats: Annotated[ChatLayer, Depends(get_chat_layer)],
                            limit: int = Query(50, ge=1, le=200),
                            offset: int = Query(0, ge=0)):
    """
    Full history, newest page first, oldest message first inside the page
    """
    chat = await chats.get_chat(chat_id)

    if not chat or chat.get('user_id') != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='CHAT_NOT_FOUND: Chat not found')

    messages = await Message.filter(chat_id=chat_id) \
                            .order_by('-id') \
                            .limit(limit) \
                            .offset(offset)

    return ChatMessagesResponseDTO(items=[ChatMessageDTO.model_validate(message)
                                          for message in reversed(messages)])
