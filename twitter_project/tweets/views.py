from django.views.generic import TemplateView
from tweets import forms, models, helpers
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse


class MainPage(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweet_form"] = forms.TweetForm
        context['images_form'] = forms.ImagesForm
        context['gif_list'] = models.Gif_Category.objects.all()

        user = self.request.user
        context['tweet_list'] = helpers.get_tweet_list(user.profile)
        return context

    def post(self, request):
        tweet_form = forms.TweetForm(request.POST)

        # TODO: Add error handling when form is incorrect
        if tweet_form.is_valid():
            tweet = tweet_form.save(commit=False)
            profile = request.user.profile
            tweet.author = profile

            # check if there are any pictures attached
            if request.POST.get("image_1"):
                images_dict = helpers.convert_images(request.POST)
                images = models.Images(**images_dict)
                images.save()
                tweet.images = images

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


def get_gifs_AJAX(request):
    query = request.GET.get("query")
    offset = request.GET.get("offser")
    limit = request.GET.get("limit")

    context = {"gif_list": helpers.get_giphy(query=query,
                                             offset=offset,
                                             limit=limit)}
    rendered_template = render(request=request,
                               template_name="tweets/gif_list.html",
                               context=context)
    return HttpResponse(rendered_template)


def get_tweets_AJAX(request):
    profile = request.user.profile
    context = {'tweet_list': helpers.get_tweet_list(profile)}
    rendered_template = render(request=request,
                               template_name="tweets/tweet_list.html",
                               context=context)
    return HttpResponse(rendered_template)
