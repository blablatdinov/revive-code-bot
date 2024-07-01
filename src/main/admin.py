from django.contrib import admin

from main.models import GhInstallation, GhRepo, TouchRecord

admin.site.register(GhInstallation)
admin.site.register(GhRepo)
admin.site.register(TouchRecord)
