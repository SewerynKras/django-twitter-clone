from django.views.generic import TemplateView
from tweets import models, helpers
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse


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
    errors = helpers.parse_new_tweet(request)
    return JsonResponse(errors)


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
