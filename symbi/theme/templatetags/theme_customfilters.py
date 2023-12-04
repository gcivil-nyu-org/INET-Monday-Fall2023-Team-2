from django import template
from main.models import Notification

register = template.Library()


@register.filter
def count_unread_notifications(user):
    return Notification.count_unread_notifications(user)
