from .models import Rubric, Article

def rubrics(request):
    return {'rubrics': Rubric.objects.all()}