from django.urls import path
from profiles import views


app_name = "profiles"

urlpatterns = [
    path("p/<slug>", views.ProfileView.as_view(), name="profile"),
    path("signup/", views.SignupView.as_view())
]
