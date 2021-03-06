from django.urls import path
from tweets import views


app_name = "tweets"


urlpatterns = [
    path("home/", views.MainPage.as_view(), name='homepage'),
    path("<slug:username>/status/<slug:tweet_id>", views.SingleTweet.as_view(), name='single_tweet'),
    path("ajax/like_tweet/", views.like_tweet_AJAX, name="like_tweet"),
    path("ajax/get_gifs/", views.get_gifs_AJAX, name="get_gifs"),
    path("ajax/get_tweets/", views.get_tweets_AJAX, name="get_tweets"),
    path("ajax/new_tweet/", views.new_tweet_AJAX, name="new_tweet"),
    path("ajax/choose_poll_option/", views.choose_poll_option_AJAX, name="choose_poll_option"),
    path("ajax/get_single_tweet/", views.get_single_tweet_AJAX, name="get_single_tweet"),
    path("ajax/get_new_tweet_form/", views.get_new_tweet_form_AJAX, name="get_new_tweet_form"),
    path("ajax/rt/", views.rt_AJAX, name='rt'),
    path("ajax/get_gif_categories/", views.get_gif_categories_AJAX, name='get_gif_categories'),
    path("search", views.SearchPage.as_view(), name='search'),
    path("compose/tweet/", views.MainPage.as_view()),
]
