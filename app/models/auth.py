from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(BaseModel):
    id: str
    email: EmailStr
    password_hash: str


class OAuthUrlResponse(BaseModel):
    url: str


class GoogleAuthCodeRequest(BaseModel):
    code: str
