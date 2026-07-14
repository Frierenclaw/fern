from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.livekit.transport import LiveKitTransport
from pipecat.turns.user_start import WakePhraseUserTurnStartStrategy
from pipecat.turns.user_turn_strategies import (
    UserTurnStrategies,
    default_user_turn_start_strategies,
)
from pipecat.workers.runner import WorkerRunner

from api.v1.bot.tool_bridge import ClientToolBridge
from api.v1.bot.tts.cartesia import VisemeCartesiaTTSService
from api.v1.bot.tts.viseme_processor import VRMVisemeProcessor
from api.v1.bot.utils import build_tools
from api.v1.heiter.tts import HeiterTTSService
from core.clients import create_stt, create_vad
from core.config import config
from models.client import Client


async def run_bot(
    transport: LiveKitTransport,
    prompt: str,
    wake_phrases: list[str],
    client: Client | None = None,
    animations: list[str] | None = None,
):
    runner = WorkerRunner()
    bridge = ClientToolBridge(transport)

    stt = create_stt()
    vad = create_vad()

    async def client_tool_handler(params: FunctionCallParams):
        result = await bridge.call(params.tool_call_id, params.function_name, dict(params.arguments))
        await params.result_callback(result)

    async def animation_tool_handler(params: FunctionCallParams):
        result = await bridge.call(params.tool_call_id, 'play_animation', dict(params.arguments))
        await params.result_callback(result)

    llm = OpenAILLMService(
        api_key=config.HEITER_TOKEN,
        base_url=config.HEITER_BASE_URL,
        settings=OpenAILLMService.Settings(
            model=config.HEITER_MODEL_NAME,
        ),
    )
    context = LLMContext(messages=[{'role': 'system', 'content': prompt}],
                         tools=build_tools(client, animations))

    if client and client.functions:
        for function in client.functions:
            llm.register_function(function.name, client_tool_handler, cancel_on_interruption=False)
    
    if animations:
        llm.register_function("play_animation", animation_tool_handler, cancel_on_interruption=False)

    if not config.USE_CARTESIA:
        tts = HeiterTTSService(base_url=f'{config.HEITER_BASE_URL}/audio/speech')
    else:
        tts = VisemeCartesiaTTSService(
            api_key=config.CARTESIA_API_KEY,
            settings=VisemeCartesiaTTSService.Settings(
                voice=config.CARTESIA_VOICE_ID,
                model='sonic-3.5',
            ),
        )
    viseme_processor = VRMVisemeProcessor(
        transport,
        word_fallback=not config.USE_CARTESIA,
    )

    aggregators = LLMContextAggregatorPair(
        context=context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad,
            user_turn_strategies=UserTurnStrategies(
                start=[
                    WakePhraseUserTurnStartStrategy(phrases=wake_phrases),
                    *default_user_turn_start_strategies(),
                ]
            ),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            aggregators.user(),
            llm,
            tts,

            transport.output(),
            viseme_processor,
            aggregators.assistant(),
        ]
    )

    worker = PipelineWorker(
        pipeline,
        name='assistant',
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler('on_client_disconnected')
    async def on_disconnect(transport, participant):
        if participant.startswith('user-'):
            await runner.cancel()

    @transport.event_handler('on_data_received')
    async def on_data(transport, data: bytes, participant):
        logger.debug(participant)
        
        if participant.startswith('user-'):
            bridge.on_tool_result(data)

    await runner.add_workers(worker)
    await runner.run()
