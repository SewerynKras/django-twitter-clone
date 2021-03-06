from django.urls import path
from profiles import views


app_name = "profiles"


urlpatterns = [
    path("signup/", views.SignupView.as_view(), name='signup'),
    path("meta/ajax/check_email/", views.check_email_AJAX, name="check_email"),
    path("meta/ajax/register/", views.register_AJAX, name='register'),
    path("login/", views.LoginView.as_view(), name='login'),
    path("logout/", views.logout_view, name="logout"),
    path("", views.LandingPageView.as_view(), name="landing_page"),
    path("ajax/get_profile/", views.get_profile_AJAX, name='get_profile'),
    path("ajax/follow/", views.follow_AJAX, name='follow'),
    path("related_users/", views.SuggestionsView.as_view(), name='suggestions'),
    path("ajax/get_follow_suggestions/", views.get_follow_suggestions_AJAX, name='who-to-follow'),
    path("<slug:profile_id>/", views.ProfileView.as_view(), name="profile"),
]
