from django import template

register = template.Library()


@register.filter(name="taggedUsers")
def taggedUsers(text, taggedUsers):
    words = text.split()
    for i, word in enumerate(words):
        if word.startswith("@"):
            username = word[1:]
            matchingUsers = taggedUsers.filter(username=username)
            for user in matchingUsers:
                profileUrl = user.get_absolute_url()
                words[
                    i
                ] = f'<a href="{profileUrl}" class="text-blue-700">@{username}</a>'
    return " ".join(words)
