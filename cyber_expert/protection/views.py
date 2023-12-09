from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse
from .forms import ArticleForm, OrderByForm
from .models import *
from .signals import comment_answer
from auth_app.models import User



class MainView(ListView, FormView):
    template_name = 'index.html'
    queryset = Article.objects.all()
    context_object_name = 'articles'
    paginate_by = 4

    form_class = OrderByForm

    #def get(self, request, *args, **kwargs):
    #    for article in queryset:
    #        views = request.session.setdefault('views', {})
    #        count = views.get(article, 0)
    #        views[article] = count + 1
    #        request.session['views']  = views
    #        return super(MainView, self).get(request, *args, **kwargs)

    def rating_sort(self, queryset):
        sorted_article = sorted(queryset, key=lambda article: article.author.get_average_rating(), reverse=True)
        return sorted_article

    def views_sort(self, queryset):
        sorted_article = sorted(queryset,
                                key=lambda article: self.request.session.get('views').get(str(article.id), 0),
                                reverse=True)
        return sorted_article

    def get_queryset(self):
        queryset = MainView.queryset
        keys = self.request.GET.keys()
        if 'search' in keys:
            search_word = self.request.GET.get('search')
            queryset = queryset.filter(title__icontains=search_word)
            return queryset
        elif 'sort' in keys:
            sort_methods = {'rating': self.rating_sort(queryset),
                            'views': self.views_sort(queryset)}
            sort_by = self.request.GET.get('sort')
            if sort_by in sort_methods:
                sorted_article = sort_methods.get(sort_by)
                return sorted_article
        else:
            return queryset


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context


'''
def index(request):
    articles = Article.objects.all()
#    def get_average_rating(articles):
#        for article in articles:
#            rating = Rating.objects.filter(author=article.author).aggregate(ave_rating=Avg('rating'))
#            return rating.get('ave_rating')
    #users = User.objects.annotate(ave=Avg('rating__rating'))
    #for user in users:
    #    print(user.ave, user)
    #authors_id = []
    #for article in articles:
    #    authors_id.append(article.author_id)
    #users = User.objects.filter(rating__author_id__in=authors_id).aggregate(ave=Avg('rating__rating'))

    #author_rating = Rating.objects.annotate(ave_rating=Avg('rating'))
    #rating = User.objects.aggregate(ave_rating=Avg('rating__rating'))
    current_year = datetime.now().year
    return render(request, context={'articles': articles,
                                    'current_year': current_year},
                  template_name='index.html')
'''


class ArticleCreateView(CreateView):
    template_name = 'create.html'
    model = Article
    form_class = ArticleForm

    permission_required = ('protection.add_article', )

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


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'create.html'
    pk_url_kwarg = 'article_id'

    permission_required = ('protection.change_article', )

    def get_queryset(self):
        return Article.objects.filter(id=self.kwargs.get('article_id'))

    def get_success_url(self):
        return reverse('detail', kwargs={'article_id': self.object.id})


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Article
    template_name = 'delete.html'
    pk_url_kwarg = 'article_id'

    permission_required = ('protection.delete_article', )

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

    def get(self, request, *args, **kwargs):
        views = request.session.setdefault('views', {})
        article_id = str(kwargs[ArticleDetailView.pk_url_kwarg])
        count = views.get(article_id, 0)
        views[article_id] = count + 1
        request.session['views'] = views
        request.session.modified = True
        return super(ArticleDetailView, self).get(request,*args, **kwargs)

    def get_queryset(self):
        return Article.objects.filter(id=self.kwargs.get('article_id'))

    def sort_comments(self, parent_comments, comments):
        sorted_comments = []
        for parent_comment in parent_comments:
            parent_comments_list = []
            parent_comments_list.append(parent_comment)
            for comment in comments:
                if comment.parent_comment == parent_comment:
                    parent_comments_list.append(comment)
            sorted_comments.append(parent_comments_list)
        return sorted_comments

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        parent_comments = Comments.objects.filter(article=self.kwargs.get('article_id'), parent_comment=None)
        comments = Comments.objects.filter(article=self.kwargs.get('article_id'))
        sorted_comments = self.sort_comments(parent_comments, comments)
        context['sorted_comments'] = sorted_comments
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
    return render(request, context={'rubrics': rubrics},
                  template_name='base.html')


def rubric_article(request, rubric_id):
    articles = Article.objects.filter(rubric=rubric_id)
    return render(request, context={'articles': articles},
                  template_name='rubric_article.html')


@login_required
def instrument(request):
    instruments = Instruments.objects.all()
    return render(request, context={'instruments': instruments}, template_name='instruments.html')


@login_required
@permission_required('protection.add_article', raise_exception=True)
def upload_instrument(request):
    msg = 'Ваш рэйтинг недостаточен для загрузки полезных утилит'
    if request.method == 'POST':
        data = request.POST
        Instruments.objects.create(file_name=data['file_name'], instrument=data['instrument'],
                                   description=data['description'], is_confirmed=True, user_sender=request.user)
        return redirect(reverse('instrument'))
    else:
        try:
            if request.user.get_average_rating() >= 4.95:
                return render(request, 'upload_instrument.html')
            else:
                return HttpResponse(msg)
        except TypeError:
            return HttpResponse(msg)


@login_required
def download_instrument(request, instrument_id):
    file = Instruments.objects.get(id=instrument_id)
    filename = file.instrument.path
    response = FileResponse(open(filename, 'rb'))
    return response



@login_required
@permission_required('protection.add_comments', raise_exception=True)
def comment(request, article_id):
    article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        data = request.POST
        Comments.objects.create(article=article, author=request.user,
                              content=data['content'])
        return redirect(reverse('detail', kwargs={'article_id': article_id}))
    else:
        return render(request, 'comment.html')


@login_required
@permission_required(('protection.add_comments', 'protection.add_article', ), raise_exception=True)
def answer_comment(request, article_id, parent_comment_id):
    article = Article.objects.get(id=article_id)
    comment = Comments.objects.get(id=parent_comment_id)
    if request.method == 'POST':
        data = request.POST
        Comments.objects.create(article=article, author=request.user,
                              content=data['content'], parent_comment=comment)
        comment_answer.send(sender=Comments, request=request, article_id=article_id, parent_comment_id=parent_comment_id)
        return redirect(reverse('detail', kwargs={'article_id': article_id}))
    else:
        return render(request, 'answer_comment.html')


@login_required
@permission_required('protection.add_rating', raise_exception=True)
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

class FavouriteView(MainView):

    def get_queryset(self):
        queryset = super(FavouriteView, self).get_queryset()
        ids = self.request.session.get('favourites', list())
        return queryset.filter(id__in=ids)


def add_reading_list(request, article_id):
    if request.method == 'POST':
        favourites = request.session.get('favourites', list())
        favourites.append(article_id)
        request.session['favourites'] = favourites
        request.session.modified = True
    return redirect(reverse('index'))


def remove_reading_list(request, article_id):
    if request.method == 'POST':
        request.session.get('favourites').remove(article_id)
        request.session.modified = True
    return redirect(reverse('index'))