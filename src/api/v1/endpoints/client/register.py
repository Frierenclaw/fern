from typing import Annotated

from fastapi import APIRouter, Depends

from api.v1.deps.auth import get_current_user
from api.v1.schemas.client_register import RegisterClientRequestDTO
from models.client import Client, ClientFunction
from models.user import User

router = APIRouter()

@router.post('/')
async def register_client(user: Annotated[User, Depends(get_current_user)],
                          dto: RegisterClientRequestDTO):
    client, _ = await Client.update_or_create(id=dto.client.id,
                                  defaults={'user': user,
                                            'app_version': dto.client.app_version or 'unknown'})
    
    await ClientFunction.filter(client=client).delete()
    
    await ClientFunction.bulk_create([
        ClientFunction(
            client=client,
            name=function.name,
            description=function.description,
            input_schema=function.input_schema.model_dump(exclude_none=True),
        )
        for function in dto.functions
    ])

    return {'status': 'ok'}
