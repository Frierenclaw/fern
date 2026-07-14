from api.v1.bot.utils import build_animation_tool, build_tools
from pipecat.processors.aggregators.llm_context import NOT_GIVEN


class ClientFunctionStub:
    def __init__(self, name, description, input_schema):
        self.name = name
        self.description = description
        self.input_schema = input_schema


class ClientStub:
    def __init__(self, functions):
        self.functions = functions


def test_build_tools_returns_not_given_without_client_tools_or_animations():
    assert build_tools(None, None) is NOT_GIVEN


def test_build_tools_includes_client_functions_and_animation_tool():
    client = ClientStub([
        ClientFunctionStub(
            name="test_echo",
            description="Echo text",
            input_schema={
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo",
                    },
                },
                "required": ["text"],
            },
        ),
    ])

    tools = build_tools(client, ["wave", "bow"])
    schemas = tools.standard_tools

    assert [schema.name for schema in schemas] == ["test_echo", "play_animation"]
    assert schemas[0].properties["text"]["type"] == "string"
    assert schemas[0].required == ["text"]
    assert schemas[1].properties["animation"]["enum"] == ["wave", "bow"]


def test_build_animation_tool_returns_none_without_animations():
    assert build_animation_tool([]) is None
