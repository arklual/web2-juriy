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
from fuzzywuzzy import fuzz
from .models import Card, Favorite
from .schemas import CreateCard, AddFavor, Error, CardSchema, StatusOK, UpdateCardSchema
from authtoken import AuthBearer
from typing import List, Optional
from categories.models import Category

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

@router.put('/update_card', response={200: CardSchema, 409: Error, 400: Error}, auth=AuthBearer)
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
        cards = Favorite.objects.filter(user = user).order_by('-card__price') # TODO: change sort
    elif sort == 'oldest':
        cards = Favorite.objects.filter(user = user).order_by('-card__price') # TODO: change sort
    cards = cards[start:(start+count)]
    return (200, cards)

@router.get('/get_cards', response={200: List[CardSchema], 409: Error, 400: Error})
def get_cards(request, start:int, count:int, sort:str, 
              time_start: Optional[str] = None, time_finish: Optional[str] = None, 
              price_floor: Optional[int] = None, price_top: Optional[int] = None,
              category: Optional[str] = None):
    if sort not in ['recent', 'oldest', 'price_upscending', 'price_descending']:
        return (400, {'details': 'sort parameter is not correct!'})
    if time_start is None:
        time_start = '01-01-2000'
    if time_finish is None:
        time_finish = '01-01-2100'
    if price_floor is None:
        price_floor = 0
    if price_top is None:
        price_top = 10000000000
    time_start = datetime.strptime(time_start, '%m-%d-%Y').date()
    time_finish = datetime.strptime(time_finish, '%m-%d-%Y').date()
    cards = Card.objects.filter(price__gte=price_floor, price__lte=price_top).order_by('price')
    # TODO: add filter by date
    if category is not None:
        category = get_object_or_404(Category, title=category)
        cards = cards.filter(category=category)
    if sort == 'price_upscending':
        cards = cards.order_by('price')
    elif sort == 'price_descending':
        cards = cards.order_by('-price')
    elif sort == 'recent':
        cards = cards.order_by('-price')# TODO: change sort
    elif sort == 'oldest':
        cards = cards.order_by('-price')# TODO: change sort
    cards = cards[start:(start+count)]
    return (200, cards)


@router.get('/search', response={200: List[CardSchema], 409: Error, 400: Error})
def search_cards(request, req: str, start:int, count:int, sort:str, 
              time_start: Optional[str] = None, time_finish: Optional[str] = None, 
              price_floor: Optional[int] = None, price_top: Optional[int] = None,
              category: Optional[str] = None):
    if sort not in ['recent', 'oldest', 'price_upscending', 'price_descending']:
        return (400, {'details': 'sort parameter is not correct!'})
    if time_start is None:
        time_start = '01-01-2000'
    if time_finish is None:
        time_finish = '01-01-2100'
    if price_floor is None:
        price_floor = 0
    if price_top is None:
        price_top = 10000000000
    time_start = datetime.strptime(time_start, '%m-%d-%Y').date()
    time_finish = datetime.strptime(time_finish, '%m-%d-%Y').date()
    cards = Card.objects.filter(price__gte=price_floor, price__lte=price_top).order_by('price')
    # TODO: add filter by date
    if category is not None:
        category = get_object_or_404(Category, title=category)
        cards = cards.filter(category=category)
    if sort == 'price_upscending':
        cards = cards.order_by('price')
    elif sort == 'price_descending':
        cards = cards.order_by('-price')
    elif sort == 'recent':
        cards = cards.order_by('-price')# TODO: change sort
    elif sort == 'oldest':
        cards = cards.order_by('-price')# TODO: change sort
    cards = cards[start:(start+count)]
    answer_cards = []
    for card in cards:
        ratio = fuzz.WRatio(req, card.name)
        if ratio > 70:
            answer_cards.append(card)
    return (200, answer_cards)


