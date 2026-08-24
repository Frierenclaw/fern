from typing import Annotated

import orjson
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from loguru import logger
from openai import APITimeoutError, AsyncOpenAI, OpenAIError, RateLimitError
from pydantic import UUID4

from api.v1.chat_logic import ChatLayer
from api.v1.deps.auth import get_current_user
from api.v1.deps.get_chat_layer import get_chat_layer
from api.v1.deps.get_openai import get_openai
from api.v1.schemas.chat_create_completion import CreateCompletionRequestDTO
from core.clients import limiter
from core.config import config
from models.character import Character
from models.enums.message_role import MessageRoleEnum
from models.user import User

router = APIRouter()


async def _save_message(chats: ChatLayer,
                        chat_id: UUID4,
                        role: MessageRoleEnum,
                        content: str):
    try:
        await chats.append(chat_id, role, content)
    except Exception as e:
        logger.error(f'Cannot save {role.value} message of chat {chat_id}. Detail: {e}')


@router.post('/{chat_id}')
@limiter.limit('20/minute')
async def create_completion(request: Request,
                            chat_id: UUID4,
                            chats: Annotated[ChatLayer, Depends(get_chat_layer)],
                            user: Annotated[User, Depends(get_current_user)],
                            openai: Annotated[AsyncOpenAI, Depends(get_openai)],
                            dto: CreateCompletionRequestDTO):
    chat = await chats.get_chat(chat_id)

    if not chat or chat.get('user_id') != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='CHAT_NOT_FOUND: Chat not found')

    character = await Character.get_or_none(id=chat.get('character_id'))

    if not character:
        logger.warning(f'{chat_id=}, cid={chat.get("character_id")} not found')

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Unexpected error. Please try again in few minutes')

    window = await chats.get_window(chat_id) # Warms the cache, must run before append()

    messages = [{'role': 'system', 'content': character.prompt},
                *window,
                {'role': 'user', 'content': dto.message}]

    await _save_message(chats, chat_id, MessageRoleEnum.USER, dto.message)

    model = dto.model or config.HEITER_MODEL_NAME

    async def generate_stream():
        answer_chunks: list[str] = []

        try:
            stream = await openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=dto.max_tokens,
                temperature=dto.temperature,
                stream=True
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None

                if delta:
                    answer_chunks.append(delta)

                yield f"data: {chunk.model_dump_json()}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f'Streaming error for user {user.id}: {e}')

            error = orjson.dumps({'error': 'Internal error. Try again later'}).decode()
            yield f"data: {error}\n\n"

        finally:
            answer = ''.join(answer_chunks)

            if answer: # Partial answers are stored too, otherwise the history would have a hole
                await _save_message(chats, chat_id, MessageRoleEnum.ASSISTANT, answer)

    try:
        if dto.stream:
            return StreamingResponse(generate_stream(), media_type="text/event-stream")

        response = await openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=dto.max_tokens,
            temperature=dto.temperature,
            stream=False
        )

        answer = response.choices[0].message.content if response.choices else None

        if answer:
            await _save_message(chats, chat_id, MessageRoleEnum.ASSISTANT, answer)

        return response

    except RateLimitError as e:
        logger.error(f'GPT Rate limit has exceeded . Detail error: {e}. Request by user {user.id}')
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail='Global rate limit has exceeded') from e
    except APITimeoutError as e:
        logger.error(f'GPT Timeout. Detail error: {e}')
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                            detail='Internal request timeout. Try again later') from e
    except OpenAIError as e:
        logger.error(f'OpenAI Error. Detail error: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Internal error. Try again later') from e
    except Exception as e:
        logger.error(f'Unexpected error. Detail error: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Internal server error. Try again later') from e
