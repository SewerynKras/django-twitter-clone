import base64
import uuid
import urllib.request
import urllib.parse
import json
import re

from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Count, Exists, OuterRef, Q, Subquery, F
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

    # give each tweet number of comments
    tweets = tweets.annotate(comments=Count("comment", distinct=True))

    # Twitter doesn't indicate whether the user has commented on
    # a tweet or not (probably because you can comment multiple times?)

    # Give each tweet an int value indicating which option the user has selected
    selected = models.PollVote.objects.filter(author=profile, poll__media__tweet=OuterRef("pk"))
    tweets = tweets.annotate(poll_chosen=Subquery(selected.values("choice")))

    # Count votes of each poll
    tweets = tweets.annotate(poll_votes_1=Count("pk", filter=Q(media__poll__pollvote__choice=1)))
    tweets = tweets.annotate(poll_votes_2=Count("pk", filter=Q(media__poll__pollvote__choice=2)))
    tweets = tweets.annotate(poll_votes_3=Count("pk", filter=Q(media__poll__pollvote__choice=3)))
    tweets = tweets.annotate(poll_votes_4=Count("pk", filter=Q(media__poll__pollvote__choice=4)))
    tweets = tweets.annotate(total_votes=(F("poll_votes_1") +
                                          F("poll_votes_2") +
                                          F("poll_votes_3") +
                                          F("poll_votes_4")))

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
            "values": {
                "value1": ...,
                "value2": ...,
                ...
                }
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

            if type(media_type) == str:
                if media_type == "img":
                    media.type = "img"
                    pattern = re.compile(r'data:image/([a-zA-Z]+);base64,([^":]+)')

                    media_item = models.Images()
                    for name in ['image_1', 'image_2', 'image_3', 'image_4']:
                        img = values.get(name)

                        if img and type(img) == str:
                            if re.match(pattern, img):
                                img_file = base64_to_image(img)
                                setattr(media_item, name, img_file)
                            else:
                                errors.update({name: "Incorrect data"})
                elif media_type == 'gif':
                    media.type = 'gif'
                    pattern = re.compile(
                        r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+')

                    media_item = models.Gif()
                    gif_url = values.get("gif_url")
                    thumb_url = values.get("thumb_url")
                    if (type(gif_url) == str and
                            type(thumb_url) == str and
                            re.match(pattern, gif_url) and
                            re.match(pattern, thumb_url)):
                        media_item.gif_url = gif_url
                        media_item.thumb_url = thumb_url
                    else:
                        errors.update({"values": "Incorrect data"})

                elif media_type == 'poll':
                    media.type = 'poll'
                    media_item = models.Poll()
                    media_item.end_date = timezone.now()
                    for name in ['choice1_text',
                                 'choice2_text',
                                 'choice3_text',
                                 'choice4_text']:
                        option = values.get(name)
                        if option:
                            if type(option) == str:
                                setattr(media_item, name, option)
                            else:
                                errors.update({name: "Incorrect data"})
                else:
                    errors.update({"media": "Incorrect/missing media type"})

        else:
            errors.update({"values": "Incorrect/missing media values"})

    if errors == {}:
        tweet.save()
        if media:
            media.tweet = tweet
            media_item.save()
            setattr(media, media.type, media_item)
            media.save()

    return errors
