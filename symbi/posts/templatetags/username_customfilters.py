from django import template
from main.models import SocialUser

register = template.Library()

@register.filter(name = 'taggedUsers')
def taggedUsers(text, taggedUsers):
    words = text.split()
    for i, word in enumerate(words):
        if word.startswith('@'):
            username = word[1:]
            matching_users = taggedUsers.filter(username=username)
            for user in matching_users:
                profileUrl = user.get_absolute_url()
                words[i] = f'<a href="{profileUrl}">@{username}</a>'
    return ' '.join(words)