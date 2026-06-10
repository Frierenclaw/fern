from pydantic import BaseModel


class RefreshEndpointRequestDTO(BaseModel):
    refresh_token: str


class RefreshEndpointResponseDTO(BaseModel):
    access_token: str
    refresh_token: str