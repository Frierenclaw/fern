import uuid

from api.v1.endpoints.client import register as register_module
from api.v1.endpoints.client.register import register_client
from api.v1.schemas.client_register import RegisterClientRequestDTO


class FakeClient:
    update_or_create_calls = []

    @classmethod
    async def update_or_create(cls, **kwargs):
        cls.update_or_create_calls.append(kwargs)
        return "client-model", False


class FakeClientFunctionQuery:
    deleted = False

    async def delete(self):
        self.deleted = True
        FakeClientFunction.deleted = True


class FakeClientFunction:
    created_items = []
    deleted = False

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    def filter(cls, **kwargs):
        cls.filter_kwargs = kwargs
        return FakeClientFunctionQuery()

    @classmethod
    async def bulk_create(cls, items):
        cls.created_items = items


async def test_register_client_replaces_functions(monkeypatch):
    FakeClient.update_or_create_calls = []
    FakeClientFunction.created_items = []
    FakeClientFunction.deleted = False
    FakeClientFunction.filter_kwargs = None
    monkeypatch.setattr(register_module, "Client", FakeClient)
    monkeypatch.setattr(register_module, "ClientFunction", FakeClientFunction)
    user = object()
    client_id = uuid.uuid4()
    dto = RegisterClientRequestDTO(
        client={
            "id": client_id,
            "app_version": None,
        },
        functions=[
            {
                "name": "test_echo",
                "description": "Echo text",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to echo",
                        },
                    },
                    "required": ["text"],
                },
            },
        ],
    )

    result = await register_client(user, dto)

    assert result == {"status": "ok"}
    assert FakeClient.update_or_create_calls == [
        {
            "id": client_id,
            "defaults": {
                "user": user,
                "app_version": "unknown",
            },
        }
    ]
    assert FakeClientFunction.deleted is True
    assert FakeClientFunction.filter_kwargs == {"client": "client-model"}
    assert len(FakeClientFunction.created_items) == 1
    created = FakeClientFunction.created_items[0].kwargs
    assert created == {
        "client": "client-model",
        "name": "test_echo",
        "description": "Echo text",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to echo",
                },
            },
            "required": ["text"],
        },
    }
