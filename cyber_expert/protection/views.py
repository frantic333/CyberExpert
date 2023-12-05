from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from .forms import ArticleForm
from .models import *
from django.db.models import  Avg, Count
from auth_app.models import User



class MainView(ListView):
    template_name = 'index.html'
    queryset = Article.objects.all()
    context_object_name = 'articles'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context
'''
def index(request):
    articles = Article.objects.all()
    authors_id = []
    for article in articles:
        authors_id.append(article.author_id)
    users = User.objects.filter(rating__author_id__in=authors_id).aggregate(ave=Avg('rating__rating'))

    #author_rating = Rating.objects.annotate(ave_rating=Avg('rating'))
    #rating = User.objects.aggregate(ave_rating=Avg('rating__rating'))
    current_year = datetime.now().year
    return render(request, context={'articles': articles,
                                    'users': users,
                                    'current_year': current_year},
                  template_name='index.html')
'''


class ArticleCreateView(CreateView):
    template_name = 'create.html'
    model = Article
    form_class = ArticleForm

    def get_success_url(self):
        return reverse('detail', kwargs={'article_id': self.object.id})

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = self.request.user
        article.save()
        return super(ArticleCreateView, self).form_valid(form)

'''
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
'''


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'create.html'
    pk_url_kwarg = 'article_id'

    def get_queryset(self):
        return Article.objects.filter(id=self.kwargs.get('article_id'))

    def get_success_url(self):
        return reverse('detail', kwargs={'article_id': self.object.id})


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'delete.html'
    pk_url_kwarg = 'article_id'

    def get_queryset(self):
        return Article.objects.filter(id=self.kwargs.get('article_id'))

    def get_success_url(self):
        return reverse('index')
'''
def delete(request, article_id):
    Article.objects.get(id=article_id).delete()
    return redirect('index')
'''


class ArticleDetailView(DetailView):
    template_name = 'detail.html'
    context_object_name = 'article'
    pk_url_kwarg = 'article_id'

    def get_queryset(self):
        return Article.objects.filter(id=self.kwargs.get('article_id'))

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context['comments'] = Comments.objects.filter(article=self.kwargs.get('article_id'))
        #article = Article.objects.filter(id=self.kwargs.get('article_id'))
        is_estimated = Rating.objects.filter(author__article=self.kwargs.get('article_id'), estimator=self.request.user).exists()
        if not is_estimated:
            context['estimate'] = True
        return context
'''    
def detail(request, article_id):
    article = Article.objects.get(id=article_id)
    comments = Comments.objects.filter(article=article_id)
    context = {'article': article, 'comments': comments}
    is_estimated = Rating.objects.filter(author=article.author, estimator=request.user).exists()
    if not is_estimated:
        context.update({'estimate': True})
    return render(request, 'detail.html', context)
'''

def rubric(request):
    rubrics = Rubric.objects.all()
    rubric_article = {}
    for rubric in rubrics:
        rubric_article.update({rubric.name: Article.objects.filter(rubric=rubric.id).count()})
    return render(request, context={'rubric_article': rubric_article},
                  template_name='rubric.html')


def instrument(request):
    instruments = Instruments.objects.all()
    return render(request, context={'instruments': instruments}, template_name='instruments.html')


def comment(request, article_id):
    article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        data = request.POST
        Comments.objects.create(article=article, author=article.author,
                              parent_comment=data['parent_comment'], date_sent=data['date_sent'])
        return redirect('detail')
    else:
        return render(request, 'detail')


def rating(request, author_id, article_id):
    author = User.objects.get(id=author_id)
    data = request.POST
    Rating.objects.create(estimator=request.user, author=author,
                              rating=data['rating'])
    return redirect(reverse('detail', kwargs={'article_id': article_id}))

'''
def rating(request, user_id, article_id):
    author = User.objects.get(id=user_id)
    if request.method == 'POST':
        data = request.POST
        Rating.objects.create(estimator=request.user, author=author,
                              rating=data['rating'])
        return redirect(reverse('detail', kwargs={'article_id': article_id}))
    else:
        return render(request, 'rating.html')
'''