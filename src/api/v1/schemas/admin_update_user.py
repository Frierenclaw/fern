from pydantic import BaseModel, EmailStr

from models.enums.role import RoleEnum


class UpdateUserRequestDTO(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None

    role: RoleEnum | None = None