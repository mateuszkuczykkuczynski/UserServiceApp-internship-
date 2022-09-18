from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class BaseUser(BaseModel):
    countryCode: str
    dateOfBirth: str
    firstName: str
    lastName: str
    nickname: str
    gender: str
    email: str


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    countryCode: str
    dateOfBirth: str
    firstName: str
    lastName: str
    nickname: str = Field(index=True)
    gender: str
    email: str = Field(index=True)


class PostUser(BaseUser):
    pass


class GetUser(BaseUser):
    id: int
