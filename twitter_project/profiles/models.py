from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_pics",
                                    height_field=None,
                                    width_field=None,
                                    max_length=None,
                                    default='profile_pics/DEFAULT.jpg')
    background_pic = models.ImageField(upload_to="background_pics",
                                       height_field=None,
                                       width_field=None,
                                       max_length=None,
                                       default='background_pics/DEFAULT.jpg')
    sync_email = models.BooleanField(default=False)
    send_news = models.BooleanField(default=False)
    personalize_ads = models.BooleanField(default=False)
    username = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(unique=True)
    display_name = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(max_length=160, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    joined = models.DateField(auto_now=True)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.username}"
