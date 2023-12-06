from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='get_views')
@stringfilter
def get_views(article_id, request):
    views = request.session.get('views', {})
    count = views.get(article_id, 0)
    return count