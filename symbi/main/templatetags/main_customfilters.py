from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def format_time_difference(timestamp):
    now = timezone.now()
    time_difference = now - timestamp
    days = time_difference.days
    seconds = time_difference.seconds
    years, remainder = divmod(days, 365)
    months, days = divmod(remainder, 30)
    weeks, days = divmod(days, 7)
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if years > 0:
        return f"{years}y"
    elif months > 0:
        return f"{months}mo"
    elif weeks > 0:
        return f"{weeks}w"
    elif days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "Just now"
