from django.contrib import admin

from main.models import GhInstallation, GhRepo

admin.site.register(GhInstallation)
admin.site.register(GhRepo)
