from django.urls import path
from .views import *


urlpatterns = [
    path('', MainView.as_view(), name='index'),
    path('create/', ArticleCreateView.as_view(), name='create'),
    path('update/<int:article_id>', ArticleUpdateView.as_view(), name='update'),
    path('delete/<int:article_id>', ArticleDeleteView.as_view(), name='delete'),
    path('detail/<int:article_id>', ArticleDetailView.as_view(), name='detail'),
    path('rubric/', rubric, name='rubric'),
    path('instrument/', instrument, name='instrument'),
    path('comment/<int:article_id>', comment, name='comment'),
    path('rating/<int:author_id>/<int:article_id>', rating, name='rating')
]