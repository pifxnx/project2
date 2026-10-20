from pydantic import BaseModel, EmailStr, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(User):
    email: EmailStr
    fullname: str
    password: str
    organization: str | None = None


class UserResponse(User):
    fullname: str
    email: EmailStr
    organization: str | None = None
