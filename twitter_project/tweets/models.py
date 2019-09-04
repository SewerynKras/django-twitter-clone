from django.db import models


class Tweet(models.Model):
    text = models.TextField(max_length=256)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    images = models.OneToOneField("tweets.Images", on_delete=models.CASCADE,
                                  null=True, blank=True)
    gif = models.OneToOneField("tweets.Gif", on_delete=models.CASCADE,
                               null=True, blank=True)
    poll = models.OneToOneField("tweets.Poll", on_delete=models.CASCADE,
                                null=True, blank=True)
    retweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE,
                                null=True, blank=True)

    def __str__(self):
        return f"TWEET BY {self.author} (ID: {self.id})"


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
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
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
            tweet = str(self.tweet)
        else:
            tweet = "<unknown>"
        return f"POLL FOR {tweet}"


class PollVote(models.Model):
    poll = models.ForeignKey("tweets.Poll", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    choice = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VOTE FOR {self.poll} BY {self.author}"


class Images(models.Model):
    photo_1 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)
    photo_2 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)
    photo_3 = models.ImageField(upload_to="tweet_images",
                                height_field=None,
                                width_field=None,
                                max_length=None,
                                default=None,
                                blank=True,
                                null=True)
    photo_4 = models.ImageField(upload_to="tweet_images",
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
    title = models.CharField(max_length=126)
    url = models.URLField(max_length=200)

    def __str__(self):
        if hasattr(self, 'tweet'):
            tweet = str(self.tweet)
        else:
            tweet = "<unknown>"
        return f"GIF ({self.title}) FOR {tweet}"
