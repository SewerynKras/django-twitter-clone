from django.shortcuts import render
from django.views.generic import TemplateView
from tweets import forms, models, helpers


class MainPage(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_tweet_form"] = forms.NewTweetForm
        context['pool_form'] = forms.PoolForm

        user = self.request.user
        context['tweet_list'] = helpers.get_tweet_list(user.profile)
        return context
