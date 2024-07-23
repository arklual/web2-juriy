from django.shortcuts import render
from .models import Category, Subscriber
from .schemas import CategorySchema, Error, CategoryInBody, StatusOK
from typing import List
from authtoken import AuthBearer
from ninja import Router
from web2_backend.settings import SECRET_KEY
from django.shortcuts import get_object_or_404
from profiles.models import Profile

import jwt

router = Router()

# Create your views here.
@router.get("/categories", response=List[CategorySchema])
def get_categories(request):
    categories = Category.objects.all()
    return (200, categories) 

@router.get('/get_followed_categories', response = {200: List[CategorySchema], 400: Error, 409: Error}, auth=AuthBearer)
def get_followed_categories(request):
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    categories = Subscriber.objects.filter(user = user)
    return (200, categories)

@router.post('/add_category', response={201: CategorySchema, 409: Error, 400: Error}, auth=AuthBearer)
def add_category(request, add_category: CategoryInBody):
    category = Category.objects.create(title = add_category.category_name)
    category.save()
    return (201, category)

@router.post('/follow_category', response={201: StatusOK, 409: Error, 400: Error}, auth=AuthBearer)
def follow_category(request, follow_category: CategoryInBody):
    category = get_object_or_404(Category, id=follow_category.card_id)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Subscriber.objects.create(
        category = category,
        user = user
    ).save()
    return (201, {'status': 'ok'})

@router.delete('/unfollow_category', response={200: StatusOK, 409: Error, 400: Error}, auth=AuthBearer)
def unfollow_category(request, unfollow_category: CategoryInBody):
    category = get_object_or_404(Category, title=unfollow_category.category_name)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Subscriber.objects.delete(
        category = category,
        user = user
    )
    return (201, {'status': 'ok'})

@router.delete('/del_category', response={200: StatusOK, 409: Error, 400: Error}, auth = AuthBearer)
def del_category(request, delete_category: CategoryInBody):
    category = get_object_or_404(Category, title=delete_category.category_name)
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    user = get_object_or_404(Profile, id=user_id)
    Category.objects.delete(title = delete_category.category_name)
    return (201, {'status': 'ok'})