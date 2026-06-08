from livekit import api as lk_api

from core.config import config


class LiveKIT:
    def __init__(self):
        self.livekit = lk_api.LiveKitAPI(url=config.LIVEKIT_API_URL,
                            api_key=config.LIVEKIT_API_KEY,
                            api_secret=config.LIVEKIT_API_SECRET)
        
    async def create_room(self, room_name: str) -> str:
        room = await self.livekit.room.create_room(
            lk_api.CreateRoomRequest(name=room_name)
        )

        return room.name
    
    @staticmethod
    def create_token(room_name: str, participant_identity: str) -> str:
        token = lk_api.AccessToken(
            api_key=config.LIVEKIT_API_KEY,
            api_secret=config.LIVEKIT_API_SECRET
        )

        token.with_identity(participant_identity)
        token.with_grants(lk_api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        return token.to_jwt()