from django.views.generic import TemplateView
from tweets import forms, models, helpers
from django.http import JsonResponse
from django.shortcuts import redirect


class MainPage(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_tweet_form"] = forms.NewTweetForm
        context['pool_form'] = forms.PoolForm
        context['sometext'] = "AAAAA"

        user = self.request.user
        context['tweet_list'] = helpers.get_tweet_list(user.profile)
        return context

    def post(self, request):
        form = forms.NewTweetForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            profile = request.user.profile
            tweet = models.Tweet(text=text, author=profile)
            tweet.save()
            return redirect("/")


def like_tweet_AJAX(request):
    profile = request.user.profile
    tweet_id = request.GET.get("tweet_id")
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
