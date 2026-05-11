from httpx import Client

from core.config import config

heiter_http_client = Client(
    base_url=config.HEITER_BASE_URL.encoded_string()
)