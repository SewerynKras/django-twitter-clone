from django.db import models


class Tweet(models.Model):
    text = models.TextField(max_length=256)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    images = models.OneToOneField("tweets.Images", on_delete=models.SET_NULL,
                                  null=True, blank=True)
    gif = models.OneToOneField("tweets.Gif", on_delete=models.SET_NULL,
                               null=True, blank=True)
    poll = models.OneToOneField("tweets.Poll", on_delete=models.SET_NULL,
                                null=True, blank=True)
    # When the retweeted tweet gets deleted this also deletes itself,
    # this could change in the future
    retweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE,
                                null=True, blank=True)

    def __str__(self):
        return f"TWEET BY {self.author} (ID: {self.id})"

    def delete(self, *args, **kwargs):
        # delete all media connected to this tweet
        self.images.delete()
        self.gif.delete()
        self.poll.delete()
        return super().delete(*args, **kwargs)


class Follow(models.Model):
    follower = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                 related_name="follow_follower")
    following = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                  related_name="follow_following")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Like(models.Model):
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LIKE BY {self.author} FOR {self.tweet}"


class Comment(models.Model):
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

    def __str__(self):
        if hasattr(self, 'tweet'):
            parent = str(self.tweet)
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
                                default=None,
                                blank=True,
                                null=True)
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
        if hasattr(self, 'tweet'):
            tweet = str(self.tweet)
        else:
            tweet = "<unknown>"
        return f"IMAGES FOR {tweet}"


class Gif(models.Model):
    gif_url = models.URLField(max_length=300)
    thumb_url = models.URLField(max_length=300)

    def __str__(self):
        if hasattr(self, 'tweet'):
            parent = str(self.tweet)
        elif hasattr(self, 'gif_category'):
            parent = str(self.gif_category)
        else:
            parent = "<unknown>"
        return f"GIF FOR {parent}"


class Gif_Category(models.Model):
    category_name = models.CharField(max_length=16)
    gif = models.OneToOneField("tweets.Gif", on_delete=models.SET_NULL,
                               null=True)

    def __str__(self):
        return f"GIF_CATEGORY ({self.category_name})"

    def delete(self, *args, **kwargs):
        self.gif.delete()
        return super().delete(*args, **kwargs)
