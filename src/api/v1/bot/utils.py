from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.processors.aggregators.llm_context import NOT_GIVEN, NotGiven

from models.client import Client


def build_tools(client: Client | None, animations: list[str] | None) -> ToolsSchema | NotGiven:
    schemas = []
    if client and client.functions:
        schemas += [FunctionSchema(name=fn.name, description=fn.description,
                                    properties=fn.input_schema.get('properties', {}),
                                    required=fn.input_schema.get('required', [])) for fn in client.functions]
    anim_tool = build_animation_tool(animations)
    if anim_tool:
        schemas.append(anim_tool)
    return ToolsSchema(standard_tools=schemas) if schemas else NOT_GIVEN

def build_animation_tool(animations: list[str] | None) -> FunctionSchema | None:
    if not animations:
        return None
    return FunctionSchema(
        name='play_animation',
        description='Trigger a VRM animation on the client.',
        properties={
            'animation': {
                'type': 'string',
                'enum': animations,
                'description': 'Name of the animation to play.',
            }
        },
        required=['animation'],
    )