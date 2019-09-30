from django.urls import path
from profiles import views


app_name = "profiles"

urlpatterns = [
    path("p/<slug>", views.ProfileView.as_view(), name="profile"),
    path("signup/", views.SignupView.as_view(), name='signup'),
    path("ajax/check_email/", views.check_email_AJAX, name="check_email"),
    path("login/", views.LoginView.as_view(), name='login'),
    path("logout/", views.logout_view, name="logout"),
    path("", views.LandingPageView.as_view(), name="landing_page"),
]
