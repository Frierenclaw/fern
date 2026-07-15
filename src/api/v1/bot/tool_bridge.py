import asyncio
import json

from pipecat.transports.livekit.transport import LiveKitTransport


class ClientToolBridge:
    def __init__(self, 
                 transport: LiveKitTransport, 
                 timeout_secs: float = 8.0,
                 retries: int = 10):
        self._transport = transport
        self._timeout = timeout_secs
        self._retries = retries
        self._pending: dict[str, asyncio.Future] = {}

    async def call(self, tool_call_id: str, name: str, arguments: dict) -> dict:
        fut = asyncio.get_event_loop().create_future()
        self._pending[tool_call_id] = fut

        payload = json.dumps({
            'type': 'tool_call',
            'call_id': tool_call_id,
            'name': name,
            'arguments': arguments,
        })

        await self._transport.send_message(payload)

        for retry in range(self._retries):
            try:
                return await asyncio.wait_for(fut, timeout=self._timeout)
            except TimeoutError:
                if retry == self._retries:
                    return {'error': 'client_timeout'}
            
        self._pending.pop(tool_call_id, None)

    def on_tool_result(self, raw: bytes):
        msg = json.loads(raw)
        if msg.get('type') != 'tool_result':
            return
        fut = self._pending.get(msg['call_id'])
        if fut and not fut.done():
            fut.set_result(msg.get('result', {}))