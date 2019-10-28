import json
import re

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from twitter_project.logging import logger
from tweets import helpers, models
from profiles.helpers import get_single_author


class MainPage(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gif_list'] = models.GifCategory.objects.all()
        context['main_body'] = "main_page"
        return context


class SingleTweet(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gif_list'] = models.GifCategory.objects.all()
        context['main_body'] = "tweet"

        context['tweet_id'] = self.kwargs.get("tweet_id")
        context['author_username'] = self.kwargs.get("username")
        return context


def get_new_tweet_form_AJAX(request):
    retweet_to = request.GET.get("retweet_to")
    if retweet_to:
        retweet_to = models.Tweet.objects.get(pk=retweet_to)
    context = {'retweet_to': retweet_to}
    template = render(request, "tweets/new_tweet.html", context=context)
    return HttpResponse(template)


def like_tweet_AJAX(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"user": "User not logged in."}, status=401)
        profile = request.user.profile
        tweet_id = request.POST.get("tweet_id")
        try:
            tweet = models.Tweet.objects.get(pk=tweet_id)
        except (ObjectDoesNotExist, ValidationError):
            return JsonResponse({"tweet_id": "This tweet doesn't exists."}, status=403)
        # check if the user has already liked this tweet
        like = models.Like.objects.filter(tweet=tweet, author=profile)
        if like.exists():
            like.delete()
            liked = False
        else:
            new_like = models.Like(author=profile, tweet=tweet)
            new_like.save()
            liked = True
        return JsonResponse({"liked": liked})
    else:
        return JsonResponse({}, status=405)


def get_gifs_AJAX(request):
    if request.method == "GET":
        query = request.GET.get("query")
        offset = request.GET.get("offset")
        limit = request.GET.get("limit")

        if query and limit and offset:

            try:
                offset = int(offset)
                limit = int(limit)
            except ValueError:
                return HttpResponse(status=400)

            if (0 <= offset <= 20) and (0 < limit <= 20):

                context = {"gif_list": helpers.get_giphy(query=query,
                                                         offset=offset,
                                                         limit=limit)}
                rendered_template = render(request=request,
                                           template_name="tweets/gif_list.html",
                                           context=context)
                return HttpResponse(rendered_template)

    return HttpResponse(status=400)


def get_tweets_AJAX(request):
    profile = request.user.profile

    auth_id = request.GET.get("single_author")
    if auth_id:
        auth = get_single_author(auth_id)
        tweets = helpers.get_tweet_list_by_single_auth(auth)
    else:
        tweets = helpers.get_tweet_list(profile)

    tweets = helpers.annotate_tweets(tweets, profile)
    context = {'tweet_list': tweets}
    rendered_template = render(request=request,
                               template_name="tweets/tweet_list.html",
                               context=context)
    return HttpResponse(rendered_template)


def get_single_tweet_AJAX(request):
    tweet_id = request.GET.get("tweet_id")
    minified = request.GET.get("minified")
    minified = True if minified == "true" else False

    profile = request.user.profile
    tweet = helpers.get_single_tweet(tweet_id)
    tweet = helpers.annotate_tweets(tweet, profile)[0]

    context = {'tweet': tweet}

    if minified:
        context['hide_media'] = True
        context['hide_buttons'] = True
    else:
        comments = helpers.get_comments(tweet)
        comments = helpers.annotate_tweets(comments, profile)
        context['comments'] = comments
        context['show_full_info'] = True

    rendered_template = render(request=request,
                               template_name="tweets/single_tweet.html",
                               context=context)
    return HttpResponse(rendered_template)


def new_tweet_AJAX(request):
    errors = {}
    if request.method == "POST":
        if not request.user.is_authenticated:
            errors['user'] = 'User not logged in.'
            return JsonResponse(errors, status=401)

        data = json.loads(request.body)

        text = data.get("text")
        if not text:
            errors['text'] = "Incorrect/missing value."
        elif len(text) > 264:
            errors['text'] = "Maximum length is 264."

        retweet_id = data.get("retweet_id")
        if retweet_id:
            if len(retweet_id) == 36:
                try:
                    models.Tweet.objects.get(id=retweet_id)
                except ObjectDoesNotExist:
                    errors["retweet"] = "Incorrect retweet id."
            else:
                errors["retweet"] = "Incorrect retweet id."

        media = data.get("media")
        if media:
            if type(media) == dict:
                media_type = media.get("type")
                values = media.get("values")
                if type(values) == dict:

                    if media_type == "img":
                        pattern = re.compile(
                            r'data:image/([a-zA-Z]+);base64,([^":]+)')

                        for name in ['image_1', 'image_2', 'image_3', 'image_4']:
                            img = values.get(name)

                            if img:
                                if not re.match(pattern, img):
                                    errors[name] = "Incorrect data."
                    elif media_type == 'gif':
                        pattern = re.compile(
                            r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+')

                        gif_url = values.get("gif_url")
                        thumb_url = values.get("thumb_url")
                        if (not gif_url or
                            not thumb_url or
                            not re.match(pattern, gif_url) or
                            not re.match(pattern, thumb_url)):

                            errors["values"] = "Incorrect data."

                    elif media_type == 'poll':
                        for name in ['choice1_text',
                                     'choice2_text',
                                     'choice3_text',
                                     'choice4_text']:
                            choice = values.get(name)
                            if choice:
                                if len(choice) > 25:
                                    errors[name] = "Maximum length is 25."

                        days = values.get("days_left")
                        try:
                            days = int(days)
                            if not 0 <= days <= 7:
                                raise ValueError
                        except (ValueError, TypeError):
                            errors['days_left'] = "Incorrect value."

                        hours = values.get("hours_left")
                        try:
                            hours = int(hours)
                            if not 0 <= hours <= 23:
                                raise ValueError
                        except (ValueError, TypeError):
                            errors['hours_left'] = "Incorrect value."

                        minutes = values.get("minutes_left")
                        try:
                            minutes = int(minutes)
                            if not 0 <= minutes <= 59:
                                raise ValueError
                        except (ValueError, TypeError):
                            errors['minutes_left'] = "Incorrect value."
                        if minutes + hours + days == 0:
                            errors['values'] = "Incorrect time values."
                    else:
                        errors["media"] = "Incorrect/missing media type."
                else:
                    errors['values'] = "Missing/Incorrect values dictionary."
            else:
                errors["media"] = "Incorrect media dictionary."
        if errors == {}:
            tweet = helpers.parse_new_tweet(data, request.user.profile)
            return JsonResponse({"id": tweet.id}, status=200)
        return JsonResponse(errors, status=400)

    return JsonResponse({}, status=405)


def choose_poll_option_AJAX(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"user": "User not logged in."}, status=401)
        profile = request.user.profile
        choice = request.POST.get("choice")
        if choice and choice not in ["1", "2", "3", "4"]:
            return JsonResponse({"choice": "Invalid choice."}, status=403)

        tweet_id = request.POST.get("tweet_id")
        try:
            tweet = models.Tweet.objects.get(pk=tweet_id)
        except (ObjectDoesNotExist, ValidationError):
            return JsonResponse({"tweet_id": "This tweet doesn't exists."}, status=403)

        poll = models.Poll.objects.filter(media__tweet=tweet).first()

        if not poll:
            return JsonResponse({"tweet_id": "This tweet doesn't have a poll."})

        if poll.has_ended:
            return JsonResponse({}, status=410)

        # check if the user has already voted on this poll
        vote = models.PollVote.objects.filter(poll=poll,
                                              author=profile).first()
        voted = None

        if vote:
            vote.delete()

        if choice:
            new_vote = models.PollVote(author=profile, poll=poll, choice=choice)
            new_vote.save()
            voted = choice

        return JsonResponse({"voted": voted})
    else:
        return JsonResponse({}, status=405)


def rt_AJAX(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"user": "User not logged in."}, status=401)

        profile = request.user.profile
        tweet_id = request.POST.get("tweet_id")

        try:
            tweet = models.Tweet.objects.get(pk=tweet_id)
        except (ObjectDoesNotExist, ValidationError):
            return JsonResponse({"tweet_id": "This tweet doesn't exists."},
                                status=403)

        new_tweet = models.Tweet(text=None, retweet_to=tweet, author=profile)
        new_tweet.save()
        return JsonResponse({})
    else:
        return JsonResponse({}, status=405)
