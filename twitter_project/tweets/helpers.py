import base64
import uuid
import urllib.request
import urllib.parse
import json
import re

from django.core.files.base import ContentFile
from django.db.models import Count, Exists, OuterRef, Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from tweets import models
from twitter_project.logging import logger


def get_tweet_list(profile, before=None, after=None):
    following = models.Follow.objects.filter(follower=profile).values("following")
    tweets = models.Tweet.objects.filter(Q(author__in=following) | Q(author=profile))

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
    is_rt_by_user = models.Tweet.objects.filter(retweet=OuterRef("id"), author=profile)
    tweets = tweets.annotate(is_rt=Exists(is_rt_by_user))

    # now the same thing for comments

    # give each tweet number of retweets
    tweets = tweets.annotate(comments=Count("comment", distinct=True))

    # Twitter doesn't indicate whether the user has commented on
    # a tweet or not (probably because you can comment multiple times?)

    tweets = tweets.order_by("-date")
    return tweets


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


def convert_images(request):
    """
    Converts all base64-encoded images from a request to image files

    Returns:
        images {dict}
    """
    images = {}
    for img in ['image_1', 'image_2', 'image_3', 'image_4']:
        if request.get(img):
            images[img] = base64_to_image(request.get(img))
    return images


def get_giphy(query, limit=1, offset=0):

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
    thumb_url = data['images']['original_still']['url']
    gif_url = data['images']['original']['url']
    gif = models.Gif(thumb_url=thumb_url,
                     gif_url=gif_url)
    return gif


def parse_new_tweet(request):
    """
    {
        "text": ...,
        "retweet": ...,
        "media": {
            "type": ...,
            "values": [
                "value1": ...,
                "value2": ...,
                ...
                ]
            }
    }
    """
    errors = {}

    if not request.user.is_authenticated:
        errors['user'] = "User not logged in"
        return errors

    data = json.loads(request.body)

    tweet = models.Tweet()
    media = None

    tweet.author = request.user.profile

    retweet_id = data.get("retweet")
    if retweet_id:
        if type(retweet_id) == str:
            try:
                retweet = models.Tweet.objects.get(id=retweet_id)
                tweet.retweet = retweet
            except ObjectDoesNotExist:
                retweet = None
                errors.update({"retweet": "Incorrect retweet id"})
        else:
            errors.update({"retweet": "Incorrect retweet id"})

    text = data.get("text")
    tweet.text = text

    try:
        tweet.full_clean()
    except ValidationError as e:
        errors.update(e.message_dict)

    request_media = data.get("media")
    if request_media and type(request_media) == dict:

        values = request_media.get("values")
        if values and type(values) == dict:

            media = models.Media()
            media_type = request_media.get("type")

            if media_type == "img":
                media.type = "img"
                pattern = re.compile(r'data:image/([a-zA-Z]+);base64,([^":]+)')

                images = models.Images()
                for name in ['image_1', 'image_2', 'image_3', 'image_4']:
                    img = values.get(name)

                    if img and type(img) == str:
                        if re.match(pattern, img):
                            img_file = base64_to_image(img)
                            setattr(images, name, img_file)
                        else:
                            errors.update({name: "Incorrect data"})
                images.save()
                media.img = images
            else:
                errors.update({"media": "Incorrect/missing media type"})

        else:
            errors.update({"values": "Incorrect/missing media values"})

    if errors == {}:
        tweet.save()
        if media:
            media.tweet = tweet
            media.save()

    return errors
