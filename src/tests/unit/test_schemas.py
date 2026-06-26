"""
Unit tests for all Pydantic schemas (DTOs).
"""
from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from api.v1.schemas.auth_refresh import RefreshEndpointRequestDTO, RefreshEndpointResponseDTO
from api.v1.schemas.auth_register import RegisterDTO
from api.v1.schemas.base_dtos import CharacterDTO, UserDTO
from api.v1.schemas.create_room import CreateRoomDTO
from api.v1.schemas.frieren_hub_create import CharacterCreateDTO, CharacterCreateResponseDTO
from api.v1.schemas.frieren_hub_get import CharacterListResponseDTO
from api.v1.schemas.frieren_hub_update import CharacterUpdateDTO, CharacterUpdateResponseDTO
from models.enums.role import RoleEnum

VALID_UUID = uuid.uuid4()


class TestUserDTO:
    def test_valid(self):
        dto = UserDTO(id=VALID_UUID, full_name="Alice")
        assert dto.full_name == "Alice"

    def test_from_attributes(self):
        assert UserDTO.model_config.get("from_attributes") is True


class TestCharacterDTO:
    def test_valid(self):
        dto = CharacterDTO(
            id=VALID_UUID, name="Frieren", description="Mage",
            cover_url=None, model_url=None,
            created_by=UserDTO(id=VALID_UUID, full_name="Author"),
        )
        assert dto.name == "Frieren"

    def test_with_likes(self):
        dto = CharacterDTO(
            id=VALID_UUID, name="F", description="D",
            cover_url=None, model_url=None, likes=42,
            created_by=UserDTO(id=VALID_UUID, full_name="A"),
        )
        assert dto.likes == 42


class TestRegisterDTO:
    def test_valid(self):
        dto = RegisterDTO(email="a@b.com", full_name="Alice", password="pass")
        assert dto.email == "a@b.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            RegisterDTO(email="not-email", full_name="A", password="p")


class TestRefreshEndpointRequestDTO:
    def test_valid(self):
        dto = RefreshEndpointRequestDTO(refresh_token="tok123")
        assert dto.refresh_token == "tok123"


class TestRefreshEndpointResponseDTO:
    def test_valid(self):
        dto = RefreshEndpointResponseDTO(access_token="a", refresh_token="r")
        assert dto.access_token == "a"


class TestCreateRoomDTO:
    def test_valid(self):
        dto = CreateRoomDTO(character_id=VALID_UUID, wake_words=["привет"])
        assert dto.character_id == VALID_UUID

    def test_empty_wake_words(self):
        dto = CreateRoomDTO(character_id=VALID_UUID, wake_words=[])
        assert dto.wake_words == []


class TestCharacterCreateDTO:
    def test_valid(self):
        dto = CharacterCreateDTO(name="Frieren", description="Mage", prompt="You are")
        assert dto.name == "Frieren"

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            CharacterCreateDTO(name="x" * 129, description="d", prompt="p")

    def test_description_too_long(self):
        with pytest.raises(ValidationError):
            CharacterCreateDTO(name="n", description="x" * 2049, prompt="p")

    def test_prompt_too_long(self):
        with pytest.raises(ValidationError):
            CharacterCreateDTO(name="n", description="d", prompt="x" * 4097)


class TestCharacterCreateResponseDTO:
    def test_valid(self):
        dto = CharacterCreateResponseDTO(character_id=VALID_UUID)
        assert dto.character_id == VALID_UUID


class TestCharacterListResponseDTO:
    def test_valid(self):
        dto = CharacterListResponseDTO(items=[], total=0)
        assert dto.total == 0


class TestCharacterUpdateDTO:
    def test_valid_empty(self):
        dto = CharacterUpdateDTO(character_id=VALID_UUID)
        assert dto.name is None

    def test_valid_partial(self):
        dto = CharacterUpdateDTO(character_id=VALID_UUID, name="New")
        assert dto.name == "New"

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            CharacterUpdateDTO(character_id=VALID_UUID, name="x" * 129)


class TestCharacterUpdateResponseDTO:
    def test_valid(self):
        dto = CharacterUpdateResponseDTO(character_id=VALID_UUID)
        assert dto.character_id == VALID_UUID


class TestRoleEnum:
    def test_values(self):
        assert RoleEnum.ADMIN.value == "admin"
        assert RoleEnum.USER.value == "user"
