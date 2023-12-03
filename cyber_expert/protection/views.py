from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.urls import reverse
from .models import *
from auth_app.models import User


def index(request):
    articles = Article.objects.all()
    current_year = datetime.now().year
    return render(request, context={'articles': articles,
                                    'current_year': current_year},
                  template_name='index.html')


def create(request):
    if request.method == 'POST':
        data = request.POST
        Article.objects.create(title=data['title'], author=request.user,
                              rubric=data['rubric'], date_added=data['date_added'],
                              content=data['content'], image=data['image'])
        return redirect('index')
    else:
        rubrics = Rubric.objects.all()
        return render(request, context={'rubrics': rubrics}, template_name='create.html')


def delete(request, article_id):
    Article.objects.get(id=article_id).delete()
    return redirect('index')


def detail(request, article_id):
    article = Article.objects.get(id=article_id)
    comments = Comments.objects.filter(article=article_id)
    context = {'article': article, 'comments': comments}
    return render(request, 'detail.html', context)


def rubric(request):
    return HttpResponse(f'Здесь будут показаны рубрики с количеством статей в каждой из них')


def instrument(request):
    instruments = Instruments.objects.all()
    return render(request, context={'instruments': instruments}, template_name='instrument.html')


def comment(request, article_id):
    article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        data = request.POST
        Comments.objects.create(article=article, author=article.author,
                              parent_comment=data['parent_comment'], date_sent=data['date_sent'])
        return redirect('detail')
    else:
        return render(request, 'detail')


def rating(request, user_id, article_id):
    author = User.objects.get(id=user_id)
    article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        data = request.POST
        Rating.objects.create(estimator=request.user, author=author,
                              rating=data['rating'])
        return redirect(reverse('detail', kwargs={'article': article}))
    else:
        return render(request, 'rating.html')