"""
All functions defined in this file expect valid data and should
not be called on raw request data!
"""
import base64
import uuid
import urllib.request
import urllib.parse
import json

from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Exists, OuterRef, Q, Subquery
from django.conf import settings

from tweets import models
from profiles.models import Follow
from twitter_project.logging import logger


def annotate_tweets(tweets, profile):
    """
    Gives each tweet in the queryset the following values:
    [1] is_liked {bool} -- has this profile liked this tweet?
    [2] is_rt {bool} -- has this profile retweeted this tweet?
    [3] poll_chosen {int} -- which option in a poll has this profile selected?

    Arguments:
        tweets {Queryset}
        profile {Profile}

    Returns:
        Queryset
    """
    logger.debug(f"Annotating tweets for {profile}")

    # [1]
    # give each tweet a bool value whether the user has liked the
    # tweet before or not
    is_liked_by_user = models.Like.objects.filter(tweet=OuterRef("id"), author=profile)
    tweets = tweets.annotate(is_liked=Exists(is_liked_by_user))

    # [2]
    # give each tweet a bool value whether the user has retweeted the
    # tweet before or not
    is_rt_by_user = models.Tweet.objects.filter(retweet_to=OuterRef("id"), author=profile)
    tweets = tweets.annotate(is_rt=Exists(is_rt_by_user))

    # NOTE:
    # Twitter doesn't indicate whether the user has commented on
    # a tweet or not (probably because you can comment multiple times?)

    # [3]
    # Give each tweet an int value indicating which option the user has selected
    selected = models.PollVote.objects.filter(author=profile, poll__media__tweet=OuterRef("pk"))
    tweets = tweets.annotate(poll_chosen=Subquery(selected.values("choice")))

    return tweets


def get_comments(tweet, before=None, after=None):
    """
    Queries all comments of the given tweet.
    Resulting queryset is reverse ordered by date.

    Arguments:
        tweet {Tweet}

    Keyword Arguments:
        before {datetime} -- (default: {None})
        after {datetime} -- (default: {None})

    Returns:
        Queryset
    """
    logger.debug(f"Getting comments for tweet: {tweet}")

    comments = models.Tweet.objects.filter(comment_to=tweet)

    if before:
        # lt == less than == before
        comments = comments.filter(date__lt=before)

    if after:
        # gt == greater than == after
        comments = comments.filter(date__gt=after)

    comments = comments.order_by("-date")
    return comments


def get_tweet_list(profile, before=None, after=None):
    """
    Queries all tweets based on the given profiles following.
    Resulting queryset is reverse ordered by date.

    Arguments:
        profile {Profile}

    Keyword Arguments:
        before {Tweet}
        after {Tweet}

    Returns:
        Queryset
    """
    logger.debug(f"Getting tweet list for {profile}")

    following = Follow.objects.filter(follower=profile).values("following")
    tweets = models.Tweet.objects.filter(Q(author__in=following) | Q(author=profile))

    if before:
        # lt == less than == before
        tweets = tweets.filter(date__lt=before.date)

    if after:
        # gt == greater than == after
        tweets = tweets.filter(date__gt=after.date)

    tweets = tweets.order_by("-date")
    return tweets


def get_tweet_list_by_single_auth(author, before=None, after=None):
    """
    Queries all tweets based on the given author.
    (This is used mostly in profile previews).
    Resulting queryset is reverse ordered by date.

    Arguments:
        author {Profile}

    Keyword Arguments:
        before {datetime} -- (default: {None})
        after {datetime} -- (default: {None})

    Returns:
        Queryset
    """
    logger.debug(f"Getting tweet list by {author}")

    tweets = models.Tweet.objects.filter(author=author)

    if before:
        # lt == less than == before
        tweets = tweets.filter(date__lt=before)

    if after:
        # gt == greater than == after
        tweets = tweets.filter(date__gt=after)

    tweets = tweets.order_by("-date")
    return tweets


def get_single_tweet(id):
    """
    Queries a single tweet with the given id.
    NOTE: this returns a Queryset of length 1, not the actual Tweet

    Arguments:
        id {str}

    Returns:
        Queryset
    """
    return models.Tweet.objects.filter(id=id)


def base64_to_image(string):
    """
    Converts a base64-encoded image into a ContentFile
    ready to be inserted into a FileField

    Example input:
        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAA...
    """
    format, image = string.split(";base64,")
    name, ext = format.split("/")

    file = ContentFile(base64.b64decode(image), name=f"{uuid.uuid4()}.{ext}")
    return file


def get_giphy(query, limit=1, offset=0):
    """
    Queries the Giphy api

    Arguments:
        query {str}

    Keyword Arguments:
        limit {int} -- (default: {1})
        offset {int} -- (default: {0})

    Returns:
        list
    """
    # Escape special characters
    query = urllib.parse.quote(query)
    gifs = []

    KEY = settings.GIPHY_API_KEY
    url = ("https://api.giphy.com/v1/gifs/search?"
           f"api_key={KEY}&"
           f"q={query}&"
           f"limit={limit}&"
           f"offset={offset}&"
           "rating=PG-13&lang=en")
    data = urllib.request.urlopen(url).read()
    data = json.loads(data)
    if data['meta']['msg'] == "OK":
        for gif_info in data['data']:
            gif = download_gif(gif_info)
            gifs.append(gif)
    return gifs


def download_gif(data):
    """
    Downloads and saves a new Gif object

    Arguments:
        data {dict} -- part of the json response provided by
            the Giphy api
    """
    logger.debug(f"Downloading gif with data: {data}")
    thumb_url = data['images']['original_still']['url']
    gif_url = data['images']['original']['url']
    gif = models.Gif(thumb_url=thumb_url,
                     gif_url=gif_url)
    return gif


def parse_new_tweet(data, profile):
    """
    Parses, creates and saves a new Tweet object alongside its Media (if applicable)

    Arguments:
        data {dict} -- JSON body
        profile {Profile}

    Returns:
        Tweet
    """
    logger.debug(f"Parsing new tweet with raw data: {data}")

    tweet = models.Tweet()
    media = None

    tweet.author = profile

    # in case the tweet is a comment
    replying_to = data.get("replying_to")
    if replying_to:
        parent_tweet = models.Tweet.objects.get(id=replying_to)
        tweet.comment_to = parent_tweet

    # in case the tweet is a retweet (with text and/or media)
    retweet_id = data.get("retweet_id")
    if retweet_id:
        retweet = models.Tweet.objects.get(pk=retweet_id)
        tweet.retweet_to = retweet

    text = data.get("text")
    tweet.text = text

    request_media = data.get("media")
    if request_media:

        # valid image media dictionary looks like the following:
        # {
        #   type: "img",
        #   values: {
        #      "image_1": "...",
        #      "image_2": "...",
        #      "image_3": "...",
        #      "image_4": "..."
        #   }
        # }

        values = request_media.get("values")

        media = models.Media()
        media_type = request_media.get("type")

        if media_type == "img":
            media.type = "img"
            media_item = models.Images()
            for name in ['image_1', 'image_2', 'image_3', 'image_4']:
                img = values.get(name)
                if img:
                    img_file = base64_to_image(img)
                    setattr(media_item, name, img_file)

        # valid gif media dictionary looks like the following:
        # {
        #   type: "gif",
        #   values: {
        #      "thumb_url": "...",
        #      "gif_url": "..."
        #   }
        # }

        elif media_type == 'gif':
            media.type = 'gif'

            media_item = models.Gif()
            gif_url = values.get("gif_url")
            thumb_url = values.get("thumb_url")

            media_item.gif_url = gif_url
            media_item.thumb_url = thumb_url

        # valid poll media dictionary looks like the following:
        # {
        #   type: "poll",
        #   values: {
        #      "choice1_text": "...",
        #      "choice2_text": "...",
        #      "choice3_text": "...",
        #      "choice4_text": "...",
        #      "days": "...",
        #      "hours": "...",
        #      "minutes": "..."
        #   }
        # }

        elif media_type == 'poll':
            media.type = 'poll'
            media_item = models.Poll()

            for name in ['choice1_text',
                         'choice2_text',
                         'choice3_text',
                         'choice4_text']:
                option = values.get(name)
                if option:
                    setattr(media_item, name, option)

            total_seconds = 0
            # convert days hours and minutes to seconds since timedelta
            # takes seconds
            days = values.get("days_left")
            total_seconds += int(days) * 24 * 60 * 60

            hours = values.get("hours_left")
            total_seconds += int(hours) * 60 * 60

            minutes = values.get("minutes_left")
            total_seconds += int(minutes) * 60

            delta = timedelta(seconds=total_seconds)
            end_date = timezone.now() + delta
            media_item.end_date = end_date

    tweet.save()
    if media:
        media.tweet = tweet
        media_item.save()
        setattr(media, media.type, media_item)
        media.save()

    return tweet
