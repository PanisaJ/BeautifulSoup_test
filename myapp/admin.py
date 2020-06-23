from django.contrib import admin

from .models import Tag, Article, Webpage

admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Webpage)
