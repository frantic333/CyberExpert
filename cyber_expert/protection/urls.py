from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('create/', create, name='create'),
    path('delete/<int:article_id>', delete, name='delete'),
    path('detail/<int:article_id>', detail, name='detail'),
    path('rubric/', rubric, name='rubric'),
    path('instrument/', instrument, name='instrument'),
    path('comment/<int:article_id>', comment, name='comment'),
    path('rating/<int:user_id>', rating, name='rating')
]