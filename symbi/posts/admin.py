# Register your models here.
from django.contrib import admin
from . models import *

admin.site.register(ActivityTag)
admin.site.register(ActivityPost)
admin.site.register(Comment)