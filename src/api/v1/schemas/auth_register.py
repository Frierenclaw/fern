from pydantic import BaseModel, EmailStr


class RegisterDTO(BaseModel):
    email: EmailStr

    full_name: str
    password: str