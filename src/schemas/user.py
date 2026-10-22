from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    email: EmailStr
    fullname: str
    password: str
    organization: str | None = None


class UserResponse(UserBase):
    fullname: str
    email: EmailStr
    organization: str | None = None
