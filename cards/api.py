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
from .schemas import CreateCard, AddFavor, Error, CardSchema, StatusOK, UpdateCardSchema
from authtoken import AuthBearer
from typing import List


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

@router.post('/add_favorite', response={201: StatusOK, 409: Error, 400: Error}, auth=AuthBearer)
def add_favorite(request, addfavor: AddFavor):
    card = get_object_or_404(Card, id=addfavor.card_id)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Favorite.objects.create(
        card = card,
        user = user
    ).save()
    return (201, {'status': 'ok'})

@router.delete('/del_favorite', response={200: StatusOK, 409: Error, 400: Error}, auth=AuthBearer)
def del_favorite(request, card_id:int):
    card = get_object_or_404(Card, id=card_id)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Favorite.objects.delete(
        card = card,
        user = user
    )
    return (201, {'status': 'ok'})

@router.post('/update_card', response={200: CardSchema, 409: Error, 400: Error}, auth=AuthBearer)
def create_card(request, create_card: UpdateCardSchema):
    data_from_wb = parse(create_card.target_url)
    c = get_object_or_404(Card, create_card.id)
    if create_card.name:
        c.name = create_card.name
    if create_card.category:
        c.category = create_card.category
    if create_card.price:
        c.price = create_card.price
    if create_card.url:
        c.url = create_card.url
    if create_card.image:
        c.image = create_card.image
    c.save()
    return (200, c)

@router.get('/get_favorite', response={200: List[CardSchema], 409: Error, 400: Error}, auth=AuthBearer)
def get_favorite(request, start:int, count:int, sort:str):
    if sort not in ['recent', 'oldest', 'price_upscending', 'price_descending']:
        return (400, {'details': 'sort parameter is not correct!'})
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    if sort == 'price_upscending':
        cards = Favorite.objects.filter(user = user).order_by('card__price')
    elif sort == 'price_descending':
        cards = Favorite.objects.filter(user = user).order_by('-card__price')
    elif sort == 'recent':
        cards = Favorite.objects.filter(user = user).order_by('-card__price')
    elif sort == 'oldest':
        cards = Favorite.objects.filter(user = user).order_by('-card__price')
    cards = cards[start:(start+count)]
    return (200, cards)