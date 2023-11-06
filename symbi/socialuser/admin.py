# Register your models here.

from django.contrib import admin
from .models import InterestTag, SocialUser, Connection

admin.site.register(InterestTag)
admin.site.register(SocialUser)
admin.site.register(Connection)
