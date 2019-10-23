from django.contrib import admin
from profiles import models


admin.site.register(models.Profile)
admin.site.register(models.Follow)
