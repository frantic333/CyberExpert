from .models import Article, Rubric
from django import forms


class ArticleForm(forms.ModelForm):
    rubric = forms.ModelChoiceField(queryset=Rubric.objects.all(), empty_label='Выберите рубрику', required=True,
                                    label='Рубрика', help_text='Выберите рубрику, к которой Вы хотите добавить статью!')

    class Meta:
        model = Article
        fields = ('title', 'rubric', 'date_added', 'content', 'image', )