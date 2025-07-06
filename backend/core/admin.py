from django.contrib import admin # type: ignore

from core import models
# Register your models here.

admin.site.register(models.Recipe)