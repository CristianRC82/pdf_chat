import datetime

from pydantic import BaseModel, EmailStr


class UserBaseDto(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: int
    birth_day: str
    photo: str


class UserDto(UserBaseDto):
    id: str
    created_at: datetime.date
    updated_at: datetime.date
    deleted_at: datetime.date


class UserUpdateDto(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    birth_day: str | None = None
    photo: str | None = None
