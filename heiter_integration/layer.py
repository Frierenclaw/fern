from openai import OpenAI

from core.config import config
from core.clients import heiter_http_client
from heiter_integration.urls import HeiterURLs
from heiter_integration.errors import HeiterLoginError, HeiterConfigNotFoundError, HeiterMissingTokenError, HeiterTokenUpdateError

from ai.prompts import SYSTEM_PROMPT

import json

class Heiter:
    """
    An neural brain
    """

    def __init__(self):
        pass

    @property
    def config(self) -> dict:
        try:
            with open('settings.json') as config_file:
                config_dict = json.load(config_file)

            return config_dict
        except Exception as e:
            raise HeiterConfigNotFoundError('Error while reading config') from e

    @property
    def api_token(self):
        if hasattr(self, '_api_token'):
            return self._api_token
        elif self.config.get('heiter_token') is not None:
            return self.config.get('heiter_token')
        else:
            raise HeiterMissingTokenError('Missing token! Please login.')
    
    @property
    def openai_client(self):
        if hasattr(self, '_openai_client'):
            return self._openai_client
        else:
            self._openai_client = OpenAI(
                base_url=config.HEITER_BASE_URL.encoded_string(),
                api_key=self.api_token)

            return self._openai_client
        
    def _update_token_in_config(self,
                                api_token: str):
        actual_config = self.config
        actual_config['heiter_token'] = api_token

        updated_config = json.dumps(actual_config)

        with open('settings.json', 'w') as config_file:
            config_file.write(updated_config)


    def login(self,
              username: str,
              password: str) -> str:
        payload = {
            'username': username,
            'password': password
        }

        response = heiter_http_client.post(
            url=HeiterURLs.LOGIN.value,
            data=payload
        )
        
        response_dict = response.json()

        if not response.is_success:
            raise HeiterLoginError(f'Error while authorizing to Heiter. Status code: {response.status_code}. Detail: {response.text}')
        
        self._api_token = response_dict.get('access_token')

        try:
            self._update_token_in_config(self._api_token)
        except Exception as e:
            raise HeiterTokenUpdateError('Token update error') from e
        
        return self._api_token


    def generate_message(self,
                         user_message: str):
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user','content': user_message}
        ]
        
        ai_response = self.openai_client.chat.completions.create(
            messages=messages,
            model='mistral-small-latest', # Расхардкодить
            metadata={'use_previous_context': True}
        )

        return ai_response.choices[0].message.content

    def synthezis_text(self,
                       input_text: str):
        ai_response = self.openai_client.audio.speech.create(
            model='edge_tts', # Расхардкодить
            input=input_text,
            voice='ru-RU-SvetlanaNeural' # Расхардкодить
        )

        for chunk in ai_response.iter_bytes():
            yield chunk