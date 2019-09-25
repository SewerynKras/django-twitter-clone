from django.db import models
import uuid


class Tweet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(max_length=256)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    # When the retweeted tweet gets deleted this also deletes itself,
    # this could change in the future
    retweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE,
                                null=True, blank=True)

    def __str__(self):
        return f"TWEET BY {self.author} (ID: {self.id})"


class Media(models.Model):
    choices = [
        ("gif", "Gif"),
        ("img", "Images"),
        ("poll", "Poll")
    ]
    type = models.CharField(max_length=10, choices=choices)
    gif = models.OneToOneField("tweets.Gif", on_delete=models.CASCADE,
                               null=True, blank=True)
    img = models.OneToOneField("tweets.Images", on_delete=models.CASCADE,
                               null=True, blank=True)
    poll = models.OneToOneField("tweets.Poll", on_delete=models.CASCADE,
                                null=True, blank=True)

    tweet = models.OneToOneField("tweets.Tweet", on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        item = getattr(self, self.type)
        item.delete()
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"MEDIA OF TYPE {self.type} FOR {self.tweet}"


class Follow(models.Model):
    follower = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                 related_name="follow_follower")
    following = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                  related_name="follow_following")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.follower} FOLLOWS {self.following}"


class Like(models.Model):
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LIKE BY {self.author} FOR {self.tweet}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=256)
    # When the original tweet gets deleted this also deletes itself,
    # this could change in the future
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    # When the replied to comment gets deleted this also deletes itself,
    # this could change in the future
    replies_to = models.ForeignKey("tweets.Comment", on_delete=models.CASCADE,
                                   null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"COMMENT BY {self.author} FOR {self.tweet}"


class Poll(models.Model):
    choice1_text = models.CharField(max_length=25)
    choice2_text = models.CharField(max_length=25)
    choice3_text = models.CharField(max_length=25, null=True, blank=True)
    choice4_text = models.CharField(max_length=25, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False)

    @property
    def total_votes(self):
        votes = PollVote.objects.filter(poll=self.pk)
        return len(votes)

    @property
    def votes1(self):
        votes = PollVote.objects.filter(poll=self.pk, choice=1)
        return len(votes)

    @property
    def votes2(self):
        votes = PollVote.objects.filter(poll=self.pk, choice=2)
        return len(votes)

    @property
    def votes3(self):
        votes = PollVote.objects.filter(poll=self.pk, choice=3)
        return len(votes)

    @property
    def votes4(self):
        votes = PollVote.objects.filter(poll=self.pk, choice=4)
        return len(votes)

    def __str__(self):
        if hasattr(self, 'media'):
            parent = str(self.media)
        else:
            parent = "<unknown>"
        return f"POLL FOR {parent}"


class PollVote(models.Model):
    poll = models.ForeignKey("tweets.Poll", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    choice = models.IntegerField(choices=((1, "choice 1"),
                                          (2, "choice 2"),
                                          (3, "choice 3"),
                                          (4, "choice 4")))
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VOTE FOR {self.poll} BY {self.author}"


class Images(models.Model):
    image_1 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                null=True,
                                blank=True)
    image_2 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)
    image_3 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)
    image_4 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)

    def __str__(self):
        if hasattr(self, 'media'):
            parent = str(self.media)
        else:
            parent = "<unknown>"
        return f"IMAGES FOR {parent}"


class Gif(models.Model):
    gif_url = models.URLField(max_length=300)
    thumb_url = models.URLField(max_length=300)

    def __str__(self):
        if hasattr(self, 'media'):
            parent = str(self.media)
        elif hasattr(self, 'gifcategory'):
            parent = str(self.gifcategory)
        else:
            parent = "<unknown>"
        return f"GIF FOR {parent}"


class GifCategory(models.Model):
    category_name = models.CharField(max_length=16)
    gif = models.OneToOneField("tweets.Gif", on_delete=models.SET_NULL,
                               null=True)

    def __str__(self):
        return f"GIFCATEGORY ({self.category_name})"

    def delete(self, *args, **kwargs):
        self.gif.delete()
        return super().delete(*args, **kwargs)
