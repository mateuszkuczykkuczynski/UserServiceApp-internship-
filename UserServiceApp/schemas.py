from pydantic import BaseModel


class UserWithoutId(BaseModel):
    countryCode: str
    dateOfBirth: str
    firstName: str
    lastName: str
    nickname: str
    gender: str
    email: str


class User(UserWithoutId):
    id: int
