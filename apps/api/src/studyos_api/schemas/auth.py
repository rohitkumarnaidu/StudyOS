"""Auth request/response models."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    display_name: str = Field(min_length=1, max_length=100)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=8, max_length=4096)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, max_length=4096)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = Field(default="Bearer")  # noqa: S105
    expires_in: int


class UserResponse(BaseModel):
    sub: str
    email: str
    display_name: str
    app_role: str = "student"
