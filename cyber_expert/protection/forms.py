from .models import Article, Rubric
from django import forms


class ArticleForm(forms.ModelForm):
    rubric = forms.ModelMultipleChoiceField(queryset=Rubric.objects.all())

    class Meta:
        model = Article
        fields = ('title', 'rubric', 'date_added', 'content', 'image', )


class OrderByForm(forms.Form):
    PRICE_CHOICES = (
        ('rating', 'рэйтинг автора'),
        ('views', 'количество просмотров'),
        )

    price_order = forms.ChoiceField(label='', choices=PRICE_CHOICES)



