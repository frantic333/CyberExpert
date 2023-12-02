from django.contrib import admin
from .models import Article, Rubric, Instruments, Comments, Rating


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'author')
    search_fields = ('title', 'date_added', 'author')
    list_per_page = 3
    actions_on_top = True
    actions_selection_counter = True
    list_display_links = ('title',)
#    filter_horizontal = ('authors',)


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    list_per_page = 3
    actions_on_top = True
    actions_selection_counter = True


@admin.register(Instruments)
class InstrumentsAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'description', 'user_sender')
    search_fields = ('file_name', 'description', 'user_sender')
    list_per_page = 3
    actions_on_top = True
    actions_selection_counter = True
    list_display_links = ('file_name',)
    list_editable = ('description',)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('article', 'parent_comment')
    search_fields = ('article', 'date_sent')
    list_per_page = 100


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating')
    search_fields = ('author', )
    list_per_page = 10