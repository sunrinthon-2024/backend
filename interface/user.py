from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    username: str
    email: str


class RegisterUserResponse(BaseModel):
    user_id: str
    username: str
    token: str


class LoginUserRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
