from datetime import datetime

from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router, Schema, Field
from django.contrib import auth
from django.db import IntegrityError
import jwt
import os
from parser_wb import parse
from profiles.models import Profile
from web2_backend.settings import SECRET_KEY

from .models import Card, Favorite
from .schemas import CreateCard, AddFavor, Error, CardSchema
from authtoken import AuthBearer

router = Router()

@router.post('/create_card', response={201: CardSchema, 409: Error, 400: Error}, auth=AuthBearer)
def create_card(request, create_card: CreateCard):
    data_from_wb = parse(create_card.target_url)
    c = Card.objects.create(
        name=data_from_wb['name'],
        url=create_card.target_url,
        image=data_from_wb['img'],
        price=data_from_wb['price'],
        category=create_card.category,
        shutdown_time=create_card.shutdown_time
    )
    c.save()
    return (201, c)

@router.post('/add_favorite', response={201: AddFavor, 409: Error, 400: Error}, auth=AuthBearer)
def create_card(request, addfavor: AddFavor):
    card = get_object_or_404(Card, id=addfavor.card_id)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Favorite.objects.create(
        card = card,
        user = user
    )
    return (201, {'status': 'ok'})