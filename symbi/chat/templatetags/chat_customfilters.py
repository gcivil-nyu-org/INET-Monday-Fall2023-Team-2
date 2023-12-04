from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def make_chat_member_list(queryset, user):
    member_names = queryset.exclude(full_name=user.full_name).values_list('full_name', flat=True)
    return ', '.join(member_names)
