from django.contrib import admin

from .models import Tag, Title, Webpage

admin.site.register(Tag)
admin.site.register(Title)
admin.site.register(Webpage)
