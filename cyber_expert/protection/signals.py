from django.dispatch import Signal
from .models import Article, Comments
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

set_views = Signal()
comment_answer = Signal()

def send_comment_answer_email(**kwargs):
    template_name = 'email/comment_answer_email.html'
    article = Article.objects.get(id=kwargs['article_id'])
    comment = Comments.objects.get(id=kwargs['parent_comment_id'])
    context = {
        'article': article,
        'message': f'На Ваш комментарий к статье {article.title} ответил автор {article.author}.'
    }
    send_mail(subject='Ответ на комментарий CyberExpert',
              message='',
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[comment.author.email],
              html_message=render_to_string(template_name, context, kwargs['request']),
              fail_silently=False)

def incr_views(sender, **kwargs):
    session = kwargs['session']
    views = session.setdefault('views', {})
    article_id = str(kwargs['id'])
    count = views.get(article_id, 0)
    views[article_id] = count + 1
    session['views'] = views
    session.modified = True

set_views.connect(incr_views)
comment_answer.connect(send_comment_answer_email)