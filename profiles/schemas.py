from ninja import Router, Schema, Field
from typing import Optional


class UserProfile(Schema):
    login: str = Field(..., min_length=1, max_length=60, required=True)
    password: str = Field(..., min_length=6, required=True)

class Error(Schema):
    details: str

class UserSignin(Schema):
    login: str = Field(..., min_length=1, max_length=60, required=True)
    password: str = Field(..., min_length=6, required=True)

class Token(Schema):
    token: str