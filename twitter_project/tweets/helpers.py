from tweets import models
from twitter_project.logging import logger
from django.db.models import Count, OuterRef, Exists


def get_tweet_list(profile, before=None, after=None):
    following = models.Follow.objects.filter(follower=profile).values("following")
    tweets = models.Tweet.objects.filter(author__in=following)

    if before:
        # lt == less than == before
        tweets = tweets.filter(date__lt=before)

    if after:
        # gt == greater than == after
        tweets = tweets.filter(date__gt=after)

    logger.debug(f"Getting tweet list for {profile}")

    # give each tweet number of likes
    tweets = tweets.annotate(likes=Count("like", distinct=True))

    # give each tweet a bool value whether the user has liked the
    # tweet before or not
    is_liked_by_user = models.Like.objects.filter(tweet=OuterRef("id"), author=profile)
    tweets = tweets.annotate(is_liked=Exists(is_liked_by_user))

    # now the same thing for retweets

    # give each tweet number of retweets
    tweets = tweets.annotate(rts=Count("retweet", distinct=True))

    # give each tweet a bool value whether the user has retweeted the
    # tweet before or not
    is_rt_by_user = models.Retweet.objects.filter(tweet=OuterRef("id"), author=profile)
    tweets = tweets.annotate(is_rt=Exists(is_rt_by_user))

    # now the same thing for comments

    # give each tweet number of retweets
    tweets = tweets.annotate(comments=Count("comment", distinct=True))

    # Twitter doesn't indicate whether the user has commented on
    # a tweet or not (probably because you can comment multiple times?)

    return tweets
