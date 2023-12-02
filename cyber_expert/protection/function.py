from django.core.exceptions import ValidationError


def tool_file_size(file):
    if file.size >= 100 * 1024 * 1024:
        raise ValidationError(message='Размер файла не должен превышать 100 Mb')