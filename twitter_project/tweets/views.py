from django.views.generic import TemplateView
from tweets import models, helpers
from django.http import JsonResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import json
import re


class MainPage(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gif_list'] = models.GifCategory.objects.all()

        user = self.request.user
        context['tweet_list'] = helpers.get_tweet_list(user.profile)
        return context


def like_tweet_AJAX(request):
    if request.method == 'POST':
        profile = request.user.profile
        tweet_id = request.POST.get("tweet_id")
        tweet = models.Tweet.objects.get(pk=tweet_id)

        # check if the user has already liked this tweet
        like = models.Like.objects.filter(tweet=tweet, author=profile)
        if like:
            like.delete()
            liked = False
        else:
            new_like = models.Like(author=profile, tweet=tweet)
            new_like.save()
            liked = True
        return JsonResponse({"liked": liked})


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
    context = {'tweet_list': helpers.get_tweet_list(profile)}
    rendered_template = render(request=request,
                               template_name="tweets/tweet_list.html",
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
            errors['text'] = "Incorrect/missing value"
        elif len(text) > 264:
            errors['text'] = "Maximum length is 264"

        retweet_id = data.get("retweet_id")
        if retweet_id:
            if len(retweet_id) == 36:
                try:
                    models.Tweet.objects.get(id=retweet_id)
                except ObjectDoesNotExist:
                    errors["retweet"] = "Incorrect retweet id"
            else:
                errors["retweet"] = "Incorrect retweet id"

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
                                    errors[name] = "Incorrect data"
                    elif media_type == 'gif':
                        pattern = re.compile(
                            r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+')

                        gif_url = values.get("gif_url")
                        thumb_url = values.get("thumb_url")
                        if (not gif_url or
                            not thumb_url or
                            not re.match(pattern, gif_url) or
                            not re.match(pattern, thumb_url)):

                            errors["values"] = "Incorrect data"

                    elif media_type == 'poll':
                        for name in ['choice1_text',
                                     'choice2_text',
                                     'choice3_text',
                                     'choice4_text']:
                            choice = values.get(name)
                            if choice:
                                if len(choice) > 25:
                                    errors[name] = "Maximum length is 25"
                    else:
                        errors["media"] = "Incorrect/missing media type"
                else:
                    errors['values'] = "Missing/Incorrect values dictionary"
            else:
                errors["media"] = "Incorrect media dictionary"
        if errors == {}:
            tweet = helpers.parse_new_tweet(data, request.user.profile)
            return JsonResponse({"id": tweet.id}, status=200)
        return JsonResponse(errors, status=400)

    return JsonResponse({}, status=405)


def choose_poll_option_AJAX(request):
    if request.method == "POST":
        profile = request.user.profile
        tweet_id = request.POST.get("tweet_id")
        choice = request.POST.get("choice")
        tweet = models.Tweet.objects.get(pk=tweet_id)

        poll = models.Poll.objects.filter(media__tweet=tweet).first()

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
