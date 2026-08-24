import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pipecat.transports.livekit.transport import LiveKitParams, LiveKitTransport

from api.v1.bot.pipeline import run_bot
from api.v1.deps.auth import get_current_user
from api.v1.livekit_logic import LiveKIT
from api.v1.schemas.create_room import CreateRoomDTO
from core.clients import limiter
from core.config import config
from models.character import Character
from models.client import Client
from models.user import User

router = APIRouter()

_bot_tasks: set[asyncio.Task] = set()


@router.post('/')
@limiter.limit('3/minute;20/hour')
async def create_room_and_invite_frieren(request: Request,
                                         user: Annotated[User, Depends(get_current_user)],
                                         dto: CreateRoomDTO):
    random_uuid = uuid.uuid4().hex
    character = await Character.get_or_none(id=dto.character_id) # TODO: add cache to redis

    client = None

    if dto.client_id:
        client = await Client.get_or_none(id=dto.client_id,
                                          user=user).prefetch_related('functions')

        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Client not found. Please register your client')

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Character not found')
    
    livekit = LiveKIT(livekit_client=request.app.state.livekit)
    room_name = await livekit.create_room(f'session-{user.id}-{random_uuid}')
    frieren_token = livekit.create_token(room_name=room_name,
                                         participant_identity=f'frieren-{random_uuid}')
    user_token = livekit.create_token(room_name=room_name,
                                      participant_identity=f'user-{user.id}')
    
    
    transport = LiveKitTransport(
        url=config.LIVEKIT_API_URL,
        token=frieren_token,
        room_name=room_name,
        params=LiveKitParams(audio_out_enabled=True,
                             audio_in_enabled=True)
    )
    
    task = asyncio.create_task(run_bot(transport=transport,
                                       prompt=character.prompt,
                                       wake_phrases=dto.wake_words,
                                       client=client,
                                       animations=dto.animations))
    _bot_tasks.add(task)
    task.add_done_callback(_bot_tasks.discard)

    return {'token': user_token,
            'livekit_url': config.LIVEKIT_URL}