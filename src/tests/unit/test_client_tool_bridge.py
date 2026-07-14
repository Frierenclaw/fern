import json
from unittest.mock import AsyncMock

import pytest

from api.v1.bot.tool_bridge import ClientToolBridge


class TestClientToolBridge:
    async def test_call_sends_tool_call_and_returns_result(self):
        transport = AsyncMock()
        bridge = ClientToolBridge(transport, timeout_secs=0.1)

        task = asyncio_create_task(bridge.call("call-1", "test_echo", {"text": "hello"}))
        await wait_for_pending_call(bridge, "call-1")

        transport.send_data.assert_awaited_once()
        payload = json.loads(transport.send_data.await_args.args[0])
        assert payload == {
            "type": "tool_call",
            "call_id": "call-1",
            "name": "test_echo",
            "arguments": {"text": "hello"},
        }
        assert transport.send_data.await_args.kwargs == {"topic": "tool_calls"}

        bridge.on_tool_result(
            json.dumps({
                "type": "tool_result",
                "call_id": "call-1",
                "result": {"ok": True, "text": "hello"},
            }).encode()
        )

        assert await task == {"ok": True, "text": "hello"}
        assert "call-1" not in bridge._pending

    async def test_call_times_out(self):
        transport = AsyncMock()
        bridge = ClientToolBridge(transport, timeout_secs=0.01)

        result = await bridge.call("call-2", "missing_tool", {})

        assert result == {"error": "client_timeout"}
        assert "call-2" not in bridge._pending

    def test_on_tool_result_ignores_non_result_messages(self):
        transport = AsyncMock()
        bridge = ClientToolBridge(transport)

        bridge.on_tool_result(json.dumps({"type": "tool_call", "call_id": "call-1"}).encode())

        assert bridge._pending == {}


def asyncio_create_task(coro):
    import asyncio

    return asyncio.create_task(coro)


async def wait_for_pending_call(bridge, call_id):
    import asyncio

    for _ in range(10):
        if call_id in bridge._pending:
            return
        await asyncio.sleep(0)
    pytest.fail(f"{call_id} was not registered as pending")
