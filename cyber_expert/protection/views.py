from django.http import HttpResponse
from django.shortcuts import render
from .models import *


def index(request):
    return HttpResponse('Здесь будет список всех статей')


def create(request):
    return HttpResponse('Здесь будет форма для создания статьи')


def delete(request, article_id):
    return HttpResponse(f'Здесь будет производится удаление {article_id} статьи')


def detail(request, article_id):
    return HttpResponse(f'Здесь мы узнаем детальную информацию о {article_id} статье')


def rubric(request):
    return HttpResponse(f'Здесь будут показаны рубрики с количеством статей в каждой из них')


def comment(request, article_id):
    return HttpResponse(f'Здесь мы сможем комментировать {article_id} статью')


def rating(request, article_id):
    article = Article.objects.get(id=article_id)
    author = article.author
    return HttpResponse(f'Здесь мы сможем оценить {author} автора статьи')