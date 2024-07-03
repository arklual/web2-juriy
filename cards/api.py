from datetime import datetime

from django.http import Http404
from ninja import Router, Schema, Field
from django.contrib import auth
from django.db import IntegrityError
import jwt
import os
from parser_wb import parse

from .models import Card
from .schemas import CreateCard, Error

router = Router()

@router.post('/create_card', response={201: CreateCard, 409: Error, 400: Error})
def create_card(request, create_card: CreateCard):
    data_from_wb = parse(create_card.target_url)
    Card.objects.create(
        name=data_from_wb['name'],
        url=create_card.target_url,
        image=data_from_wb['img'],
        price=data_from_wb['price'],
        category=create_card.category,
        shutdown_time=create_card.shutdown_time
    )