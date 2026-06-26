from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.livekit.transport import LiveKitTransport
from pipecat.turns.user_start import WakePhraseUserTurnStartStrategy
from pipecat.turns.user_turn_strategies import (
    UserTurnStrategies,
    default_user_turn_start_strategies,
)
from pipecat.workers.runner import WorkerRunner

from api.v1.bot.viseme_processor import VRMVisemeProcessor
from api.v1.heiter.tts import HeiterTTSService
from core.clients import create_stt, create_vad
from core.config import config


async def run_bot(transport: LiveKitTransport,
                  prompt: str,
                  wake_phrases: list[str]):
    runner = WorkerRunner()

    stt = create_stt()
    vad = create_vad()

    llm = OpenAILLMService(
        api_key=config.HEITER_TOKEN,
        base_url=config.HEITER_BASE_URL,
        settings=OpenAILLMService.Settings(
            model=config.HEITER_MODEL_NAME,
        ),
    )
    
    if (not config.CARTESIA_API_KEY) or (not config.CARTESIA_VOICE_ID): 
        tts = HeiterTTSService(
            base_url=f'{config.HEITER_BASE_URL}/audio/speech'
        )
    else:
        tts = CartesiaTTSService(api_key=config.CARTESIA_API_KEY,
                                settings=CartesiaTTSService.Settings(voice=config.CARTESIA_VOICE_ID))
    viseme_processor = VRMVisemeProcessor(transport)

    context = LLMContext(messages=[{'role': 'system', 'content': prompt}])

    aggregators = LLMContextAggregatorPair(context=context,
                                           user_params=LLMUserAggregatorParams(vad_analyzer=vad,
                                                                               user_turn_strategies=UserTurnStrategies(
                                                                                   start=[WakePhraseUserTurnStartStrategy(phrases=wake_phrases),
                                                                                          *default_user_turn_start_strategies()]
                                                                               )))

    pipeline = Pipeline([
        transport.input(),
    
        stt,
        aggregators.user(),
        
        llm,
        tts,
        transport.output(),
        viseme_processor,

        aggregators.assistant(),
    ])

    worker = PipelineWorker(
        pipeline,
        name='assistant',
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler('on_client_disconnected')
    async def on_disconnect(transport, client):
        await runner.cancel()

    await runner.add_workers(worker)
    await runner.run()