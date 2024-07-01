from datetime import datetime

from django.http import Http404
from ninja import Router, Schema, Field
from django.contrib import auth
from django.db import IntegrityError
import jwt
import os

from .models import Profile
from .schemas import Token, UserSignin, UserProfile, Error
from web2_backend.settings import SECRET_KEY

router = Router()

@router.post('/register', response={201: UserProfile, 409: Error, 400: Error})
def signup(request, user: UserProfile):
    account = Profile.objects.create_user(email=user.login, password=user.password)
    return 201, account


@router.post('/sign-in', response={200: Token, 404: Error, 400: Error    })
def signin(request, user: UserSignin):
    account = auth.authenticate(username=user.email, password=user.password)
    if account is not None:
        encoded_jwt = jwt.encode({"createdAt": datetime.utcnow().timestamp(), "user_id": account.id}, SECRET_KEY, algorithm="HS256")
        return 200, {"token": encoded_jwt}
    else:
        return 404, {"details": "user not found"}
