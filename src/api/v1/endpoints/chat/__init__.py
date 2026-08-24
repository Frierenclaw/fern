from fastapi import APIRouter

from api.v1.endpoints.chat import create_completions, get_messages, start_chat

base_chat_router = APIRouter(prefix='/chat')
base_chat_router.include_router(create_completions.router)
base_chat_router.include_router(get_messages.router)
base_chat_router.include_router(start_chat.router)
