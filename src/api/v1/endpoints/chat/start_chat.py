from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import UUID4

from api.v1.chat_logic import ChatLayer
from api.v1.deps.auth import get_current_user
from api.v1.deps.get_chat_layer import get_chat_layer
from api.v1.schemas.chat_start_chat import StartChatResponseDTO
from core.clients import limiter
from models.character import Character
from models.user import User

router = APIRouter()

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=StartChatResponseDTO)
@limiter.limit('5/minute;30/hour')
async def create_chat(request: Request,
                      user: Annotated[User, Depends(get_current_user)],
                      chats: Annotated[ChatLayer, Depends(get_chat_layer)],
                      character_id: UUID4):
    character_exists = await Character.filter(id=character_id,
                                              is_approved=True).exists()

    if not character_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')

    try:
        chat = await chats.create(user_id=user.id,
                                  character_id=character_id)
    except Exception as e:
        logger.exception(f'Error while trying to create chat. Detail: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Unexpected error. Please try again in few minutes')

    return StartChatResponseDTO(chat_id=chat.id)
