from django.urls import path, re_path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('create/', create, name='create'),
    path('delete/<int:article_id>', delete, name='delete'),
    re_path('^detail/(?P<article_id>[1-9][0-9])/$', detail, name='detail'),
    path('rubric/', rubric, name='rubric'),
    path('comment/<int:article_id>', comment, name='comment'),
    path('rating/<int:article_id>', rating, name='rating')
]