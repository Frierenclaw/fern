from pydantic import BaseModel


class AdminCreateUser(BaseModel):
    full_name: str
    email: str
    password: str