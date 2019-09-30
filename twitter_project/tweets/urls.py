from django.urls import path
from tweets import views


app_name = "tweets"


urlpatterns = [
    path("home/", views.MainPage.as_view(), name='homepage'),
    path("ajax/like_tweet/", views.like_tweet_AJAX, name="like_tweet"),
    path("ajax/get_gifs/", views.get_gifs_AJAX, name="get_gifs"),
    path("ajax/get_tweets/", views.get_tweets_AJAX, name="get_tweets"),
    path("ajax/new_tweet/", views.new_tweet_AJAX, name="new_tweet"),
    path("ajax/choose_poll_option/", views.choose_poll_option_AJAX, name="choose_poll_option"),
]
