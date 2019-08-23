from django.db import models
from twitter_project.logging import logger


class Tweet(models.Model):
    text = models.CharField(max_length=256)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TWEET BY {self.author}"

    def save(self, *args, **kwargs):
        logger.info(f"Created a new Tweet ({self})")
        return super().save(*args, **kwargs)


class Follow(models.Model):
    follower = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                 related_name="follow_follower")
    following = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE,
                                  related_name="follow_following")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"

    def save(self, *args, **kwargs):
        logger.info(f"New follow ({self})")
        return super().save(*args, **kwargs)


class Like(models.Model):
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LIKE BY {self.author} FOR {self.tweet}"


class Retweet(models.Model):
    text = models.CharField(max_length=256, null=True, blank=True)
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RETWEET BY {self.author} FOR {self.tweet}"

    def save(self, *args, **kwargs):
        logger.info(f"Created a new Retweet ({self})")
        return super().save(*args, **kwargs)


class Comment(models.Model):
    text = models.CharField(max_length=256)
    tweet = models.ForeignKey("tweets.Tweet", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    replies_to = models.ForeignKey("tweets.Comment", on_delete=models.CASCADE,
                                   null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"COMMENT BY {self.author} FOR {self.tweet}"

    def save(self, *args, **kwargs):
        logger.info(f"Created a new Comment ({self})")
        return super().save(*args, **kwargs)


class Poll(models.Model):
    tweet = models.OneToOneField("tweets.Tweet", on_delete=models.CASCADE)
    choice1_text = models.CharField(max_length=25,)
    choice2_text = models.CharField(max_length=25,)
    choice3_text = models.CharField(max_length=25, null=True, blank=True)
    choice4_text = models.CharField(max_length=25, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False)

    def __str__(self):
        return f"POLL FOR {self.tweet}"

    def save(self, *args, **kwargs):
        logger.info(f"Created a new Poll ({self})")
        return super().save(*args, **kwargs)


class PollVote(models.Model):
    poll = models.ForeignKey("tweets.Poll", on_delete=models.CASCADE)
    author = models.ForeignKey("profiles.Profile", on_delete=models.CASCADE)
    choice = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VOTE FOR {self.poll} BY {self.author}"

    def save(self, *args, **kwargs):
        logger.info(f"Created a new PoolVote ({self})")
        return super().save(*args, **kwargs)
