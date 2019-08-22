from django.urls import path
from tweets import views


app_name = "tweets"


urlpatterns = [
    path("", views.MainPage.as_view(), name='homepage')
]
