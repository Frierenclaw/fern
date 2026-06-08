import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pipecat.transports.livekit.transport import LiveKitParams, LiveKitTransport

from api.v1.bot.pipeline import run_bot
from api.v1.deps.auth import get_current_user
from api.v1.livekit_logic import LiveKIT
from core.config import config
from models.user import User

router = APIRouter()

_bot_tasks: set[asyncio.Task] = set()


@router.post('/')
async def create_room_and_invite_frieren(user: Annotated[User, Depends(get_current_user)]):
    random_uuid = uuid.uuid4().hex

    livekit = LiveKIT()
    room_name = await livekit.create_room(f'session-{user.id}-{random_uuid}')
    frieren_token = livekit.create_token(room_name=room_name,
                                         participant_identity=f'frieren-{random_uuid}')
    user_token = livekit.create_token(room_name=room_name,
                                      participant_identity=f'user-{user.full_name}')
    
    transport = LiveKitTransport(
        url=config.LIVEKIT_API_URL,
        token=frieren_token,
        room_name=room_name,
        params=LiveKitParams(audio_out_enabled=True,
                             audio_in_enabled=True)
    )
    
    task = asyncio.create_task(run_bot(transport))
    _bot_tasks.add(task)
    task.add_done_callback(_bot_tasks.discard)

    return {'token': user_token,
            'livekit_url': config.LIVEKIT_URL}