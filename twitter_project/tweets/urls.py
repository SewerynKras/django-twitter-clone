from django.urls import path
from tweets import views


app_name = "tweets"


urlpatterns = [
    path("", views.MainPage.as_view(), name='homepage'),
    path("ajax/like_tweet/", views.like_tweet_AJAX, name="like_tweet")
]
