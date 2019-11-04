from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.text import slugify
from random import choice


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_pics",
                                    height_field=None,
                                    width_field=None,
                                    max_length=None,
                                    default='profile_pics/DEFAULT_GRAY.png')
    background_pic = models.ImageField(upload_to="background_pics",
                                       height_field=None,
                                       width_field=None,
                                       max_length=None,
                                       default='background_pics/DEFAULT_GRAY.png')
    sync_email = models.BooleanField(default=False)
    send_news = models.BooleanField(default=False)
    personalize_ads = models.BooleanField(default=False)
    username = models.CharField(max_length=20, unique=True)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    display_name = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(max_length=160, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    joined = models.DateField(auto_now=True)
    verified = models.BooleanField(default=False)
    fake = models.BooleanField(default=False, blank=True)

    @property
    def following(self):
        return len(Follow.objects.filter(follower=self.pk))

    @property
    def followers(self):
        return len(Follow.objects.filter(following=self.pk))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        return super().save(*args, **kwargs)

    def randomize_media(self):
        """
        Changes the background_pic and profile_pic to one of the default ones
        """
        colors = ['GRAY', "BLUE", "YELLOW", "PINK", "PURPLE", "RED", "GREEN"]
        bg_color = choice(colors)
        self.background_pic = f"background_pics/DEFAULT_{bg_color}.png"

        prof_color = choice(colors)
        self.profile_pic = f"profile_pics/DEFAULT_{prof_color}.png"

    def __str__(self):
        return f"@{self.username}"


class Follow(models.Model):
    follower = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                 related_name="follow_follower")
    following = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                  related_name="follow_following")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.follower} FOLLOWS {self.following}"
