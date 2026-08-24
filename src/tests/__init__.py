"""
Global test configuration: sets env vars and generates RSA keys BEFORE
any application module is imported.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


_KEY_DIR = tempfile.mkdtemp(prefix="fern_test_keys_")
_access_pv, _access_pb = _generate_rsa_keypair()
_refresh_pv, _refresh_pb = _generate_rsa_keypair()

Path(_KEY_DIR, "access_private.pem").write_bytes(_access_pv)
Path(_KEY_DIR, "access_public.pem").write_bytes(_access_pb)
Path(_KEY_DIR, "refresh_private.pem").write_bytes(_refresh_pv)
Path(_KEY_DIR, "refresh_public.pem").write_bytes(_refresh_pb)


_ENV = {
    "DB_URL": "sqlite://:memory:",
    "HEITER_BASE_URL": "http://heiter:8000/v1/audio/speech",
    "HEITER_MODEL_NAME": "edge_tts",
    "HEITER_TOKEN": "heiter_test_token",
    "HEITER_TTS_MODEL": "edge_tts",
    "HEITER_TTS_VOICE": "ru-RU-SvetlanaNeural",
    "HEITER_TTS_LANGUAGE": "ru",
    "ENGINE_VERSION": "0.0.1",
    "ENGINE_NAME": "Fern Test",
    "LIVEKIT_URL": "wss://lk.test.com",
    "LIVEKIT_API_URL": "https://lk.test.com",
    "LIVEKIT_API_KEY": "lk_test_key",
    "LIVEKIT_API_SECRET": "a" * 32,
    "S3_ENDPOINT_URL": "https://s3.test.com",
    "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7",
    "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI",
    "BUCKET_NAME": "test-bucket",
    "S3_REGION_NAME": "us-east-1",
    "ALLOWED_COVER_EXTENSIONS": '[".jpg", ".png", ".webp"]',
    "ALLOWED_COVER_MIME_TYPES": '["image/jpeg", "image/png", "image/webp"]',
    "ALLOWED_MODEL_EXTENSIONS": '[".glb", ".vrm"]',
    "ALLOWED_MODEL_MIME_TYPES": '["model/gltf-binary", "application/octet-stream"]',
    "ALLOWED_ANIMATIONS_EXTENSIONS": '[".vrma"]',
    "ALLOWED_ANIMATIONS_MIME_TYPES": '["application/octet-stream"]',
    "ACCESS_TOKEN_TTL": "300",
    "REFRESH_TOKEN_TTL": "86400",
    "JWT_ALGO": "RS256",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_PASSWORD": "test",
    "REDIS_LIMITER_DB": "1",
    "DEEPGRAM_API_KEY": "dg_test_key",
    "DEEPGRAM_MODEL": "nova-3",
    "ACCESS_PRIVATE_KEY_PATH": str(Path(_KEY_DIR, "access_private.pem")),
    "ACCESS_PUBLIC_KEY_PATH": str(Path(_KEY_DIR, "access_public.pem")),
    "REFRESH_PRIVATE_KEY_PATH": str(Path(_KEY_DIR, "refresh_private.pem")),
    "REFRESH_PUBLIC_KEY_PATH": str(Path(_KEY_DIR, "refresh_public.pem")),
    "CARTESIA_API_KEY": "",
    "CARTESIA_VOICE_ID": "",
}

for _k, _v in _ENV.items():
    os.environ.setdefault(_k, _v)
