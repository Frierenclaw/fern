from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger

from api.v1.auth_logic.layer import Auth
from api.v1.schemas.auth_refresh import RefreshEndpointRequestDTO, RefreshEndpointResponseDTO
from core.clients import limiter

router = APIRouter()

@router.post('/refresh', response_model=RefreshEndpointResponseDTO)
@limiter.limit('30/minute')
async def refresh_endpoint(request: Request,
                           dto: RefreshEndpointRequestDTO):
    try:
        refresh_token = Auth.decode_refresh_token(dto.refresh_token)   
    except Exception as e:
        logger.warning(f'Error while decoding token. Detail: {e}')

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Ilegal token')
    
    new_access_token = Auth.generate_access_token(user_id=refresh_token.get('user_id'))
    new_refresh_token = Auth.generate_refresh_token(user_id=refresh_token.get('user_id'))

    return RefreshEndpointResponseDTO(access_token=new_access_token,
                                      refresh_token=new_refresh_token)

    # TODO: feat: add redis refresh jti blacklist