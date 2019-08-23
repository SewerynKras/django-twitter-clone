from django.contrib import admin
from tweets import models

admin.site.register(models.Tweet)
admin.site.register(models.Retweet)
admin.site.register(models.Comment)
admin.site.register(models.Poll)
admin.site.register(models.PollVote)
admin.site.register(models.Follow)
admin.site.register(models.Like)
