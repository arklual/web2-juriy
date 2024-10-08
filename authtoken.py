from django.http import Http404
import jwt
from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer

from profiles.models import Profile
from web2_backend.settings import SECRET_KEY


class InvalidToken(Exception):
    pass

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = get_object_or_404(Profile, id=user_id)
        except jwt.ExpiredSignatureError:
            raise InvalidToken
        except jwt.InvalidTokenError:
            raise InvalidToken
        return token