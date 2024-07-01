from django.contrib import admin

from main.models import GhRepo, TouchRecord

admin.site.register(GhRepo)
admin.site.register(TouchRecord)
