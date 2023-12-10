from django.apps import AppConfig


class ProtectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'protection'
    verbose_name = 'Управление содержимым сайта'

    def ready(self):
        from .signals import send_comment_answer_email
