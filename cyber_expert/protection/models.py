from django.db import models
from django.conf import settings
from .function import tool_file_size
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(verbose_name='Описание статьи', max_length=70, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Автор курса')
    rubric = models.ManyToManyField('Rubric', db_table='article_rubric', verbose_name='рубрика')
    date_added = models.DateField(verbose_name='Дата добавления')
    content = models.TextField(verbose_name='Контент статьи', max_length=10000)
    image = models.ImageField(verbose_name='Картинка', blank=True, upload_to='images')

    class Meta:
        verbose_name_plural = 'Статьи'
        verbose_name = 'Статья'
        ordering = ['title']


    def get_absolute_url(self):
        return reverse('detail', kwargs={'article_id': self.pk})

    def __str__(self):
        return f'{self.title}: Старт{self.date_added}'


class Rubric(models.Model):
    name = models.CharField(verbose_name='Название рубрики', max_length=30, unique=True)

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']


    def __str__(self):
        return f'{self.name}'


    def get_article_count(self):
        count = Article.objects.filter(rubric=self).count()
        return count


class Instruments(models.Model):
    file_name = models.CharField(verbose_name='Название файла', max_length=30, unique=True)
    instrument = models.FileField(verbose_name='Инструмент', blank=False, validators=[tool_file_size], upload_to='instruments')
    description = models.TextField(verbose_name='Возможности и характеристики', max_length=1000)
    is_confirmed = models.BooleanField(verbose_name='Безопасность подтверждена')
    user_sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Пользователь отправитель')

    class Meta:
        verbose_name_plural = 'Инструменты'
        verbose_name = 'Инструмент'
        ordering = ['file_name']


    def __str__(self):
        return f'{self.file_name}'


class Comments(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='статья')
    content = models.TextField(verbose_name='Комментарий', max_length=250)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Родительский комментарий', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Автор комментария')
    date_sent = models.DateField(auto_now_add=True, verbose_name='Дата отправки комментария')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-date_sent']


class Rating(models.Model):
    estimator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Кто оценил пользователя')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings', verbose_name='Кому поставлена оценка')
    rating = models.PositiveIntegerField(verbose_name='Оценка')

    class Meta:
        verbose_name_plural = 'Оценки'
        verbose_name = 'Оценка'
        ordering = ['rating']