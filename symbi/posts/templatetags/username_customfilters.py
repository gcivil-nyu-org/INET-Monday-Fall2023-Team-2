from django import template
from main.models import SocialUser

register = template.Library()

@register.filter(name = 'taggedUser')
def taggedUsers(text, taggedUsers):
    words = text.split()
    for i, word in enumerate(words):
        if word.startswith('@'):
            username = word[1:]
            try:
                user = taggedUsers.get(username=username)
                profileUrl = SocialUser.get_absolute_url()
                words[i] = f'<a href="{profileUrl}">@{username}</a>'
            except SocialUser.DoesNotExist:
                pass
    return ' '.join(words)
