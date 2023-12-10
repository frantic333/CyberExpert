from django.urls import path
from .views import *


urlpatterns = [
    path('', MainView.as_view(), name='index'),
    path('create/', ArticleCreateView.as_view(), name='create'),
    path('update/<int:article_id>', ArticleUpdateView.as_view(), name='update'),
    path('delete/<int:article_id>', ArticleDeleteView.as_view(), name='delete'),
    path('detail/<int:article_id>', ArticleDetailView.as_view(), name='detail'),
    path('rubric/', rubric, name='rubric'),
    path('rubric_article/<int:rubric_id>', rubric_article, name='rubric_article'),
    path('instrument/', instrument, name='instrument'),
    path('comment/<int:article_id>', comment, name='comment'),
    path('answer_comment/<int:article_id>/<parent_comment_id>', answer_comment, name='answer_comment'),
    path('rating/<int:author_id>/<int:article_id>', rating, name='rating'),
    path('upload_instrument/', upload_instrument, name='upload_instrument'),
    #path('download_instrument/<int:instrument_id>', download_instrument, name='download_instrument'),
    path('download_instrument/<int:instrument_id>', DownloadView.as_view(), name='download_instrument'),
    path('add_reading_list/<int:article_id>', add_reading_list, name='add_reading_list'),
    path('remove_reading_list/<int:article_id>', remove_reading_list, name='remove_reading_list'),
    path('favourites/', FavouriteView.as_view(), name='favourites')
]