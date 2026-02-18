from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Получить значение из словаря по ключу
    Usage: {{ dictionary|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
