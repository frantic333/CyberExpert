from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.urls import reverse
from .forms import ArticleForm, OrderByForm
from .models import *
from .signals import comment_answer
from auth_app.models import User
from django.shortcuts import get_object_or_404



class MainView(ListView, FormView):
    template_name = 'index.html'
    queryset = Article.objects.all()
    context_object_name = 'articles'
    paginate_by = 4

    form_class = OrderByForm

    def rating_sort(self, queryset, reverse=True):
        sorted_article = sorted(queryset, key=lambda article: article.author.get_average_rating(), reverse=reverse)
        return sorted_article

    def views_sort(self, queryset):
        try:
            sorted_article = sorted(queryset,
                                    key=lambda article: self.request.session.get('views').get(str(article.id), 0),
                                    reverse=True)
            return sorted_article
        except AttributeError:
            return queryset

    def get_queryset(self):
        queryset = MainView.queryset
        keys = self.request.GET.keys()
        if 'search' in keys:
            search_word = self.request.GET.get('search')
            queryset = queryset.filter(title__icontains=search_word)
            return queryset
        elif 'sort' in keys:
            sort_methods = {'rating': self.rating_sort(queryset),
                            'rating_reverse': self.rating_sort(queryset, False),
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


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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
        return Article.objects.filter(id=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        paper = self.object
        comments = Comments.objects.filter(article=paper).select_related('author').order_by('parent_comment', 'date_sent')
        context['sorted_comments'] = comments
        if not self.request.user.is_authenticated:
            context['is_estimated'] = False
        else:
            context['is_estimated'] = Rating.objects.filter(author__article=paper, estimator=self.request.user).exists()


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
        print(request.FILES)
        data = request.POST
        Instruments.objects.create(file_name=data['file_name'], instrument=request.FILES.get('instrument'),
                                   description=data['description'], is_confirmed=True, user_sender=request.user)
        return redirect(reverse('instrument'))
    else:
        if request.user.get_average_rating() >= 4.95:
            return render(request, 'upload_instrument.html')
        else:
            return HttpResponse(msg)


class DownloadView(View):
    def get(self, request,  instrument_id, *args, **kwargs):
        tool = get_object_or_404(Instruments, id=instrument_id)
        file_path = tool.instrument.path
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment;filename="{tool.file_name}"'
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