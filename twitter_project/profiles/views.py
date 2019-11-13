from django.views.generic import TemplateView
from profiles import models, forms, helpers
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from twitter_project.logging import logger
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.messages import error
from django.shortcuts import render


class ProfileView(TemplateView):
    template_name = "tweets/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_body'] = "profile"

        context['profile_id'] = self.kwargs.get("profile_id")
        return context


class SignupView(TemplateView):
    template_name = "profiles/sign_up.html"
    login_required = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.SignUpForm
        return context


class LoginView(TemplateView):
    template_name = "profiles/login.html"
    login_required = False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['login_form'] = forms.LoginForm
        return context

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/home')
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        identifier = request.POST.get("identifier")
        password = request.POST.get('password')
        try:
            user = authenticate(identifier=identifier, password=password)
        except ObjectDoesNotExist as e:
            error(request, str(e))
            return redirect("/login")

        login(request, user, backend="twitter_project.backends.CustomLoginBackend")
        # go back to the homepage
        return redirect("/home")


class LandingPageView(TemplateView):
    template_name = "profiles/landing_page.html"
    login_required = False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['login_form'] = forms.LoginForm
        return context

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/home')
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        identifier = request.POST.get("identifier")
        password = request.POST.get('password')
        try:
            user = authenticate(identifier=identifier, password=password)
        except ObjectDoesNotExist as e:
            error(request, str(e))
            return redirect("/login")

        login(request, user, backend="twitter_project.backends.CustomLoginBackend")
        # go back to the homepage
        return redirect("/home")


def logout_view(request):
    logout(request)
    return redirect("/")


def check_email_AJAX(request):
    email = request.GET.get("email")
    if not helpers.is_email_valid(email):
        error = "Please enter a valid email."
    elif not helpers.is_email_unique(email):
        error = "Email has already been taken."
    else:
        error = ""
    response = {"error": error}

    logger.debug("Email checked: " + email + " error found: " + error)

    return JsonResponse(response)


def get_profile_AJAX(request):
    if request.method == "GET":
        profile_id = request.GET.get("profile_id")
        try:
            profile = models.Profile.objects.get(username__iexact=profile_id)
        except (ObjectDoesNotExist, ValidationError):
            return HttpResponse(None, status=403)

        follower = request.user.profile
        following = profile
        is_followed = helpers.check_if_user_follows(follower=follower,
                                                    following=following)

        context = {"profile": profile, "is_followed": is_followed}
        rendered_template = render(request=request,
                                   template_name="profiles/profile.html",
                                   context=context)
        return HttpResponse(rendered_template)


def follow_AJAX(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"user": "User not logged in."}, status=401)
        follower = request.user.profile
        following_id = request.POST.get("profile_id")
        try:
            following = models.Profile.objects.get(username__iexact=following_id)
        except (ObjectDoesNotExist, ValidationError):
            return JsonResponse({"following_id": "This profile doesn't exists."}, status=403)

        if follower == following:
            return JsonResponse({"following_id": "You can't follow yourself."}, status=405)

        # check if the user has already followed this profile
        follow = models.Follow.objects.filter(follower=follower, following=following)
        if follow.exists():
            follow.delete()
            followed = False
        else:
            new_follow = models.Follow(follower=follower, following=following)
            new_follow.save()
            followed = True
        return JsonResponse({"followed": followed})
    else:
        return JsonResponse({}, status=405)


def register_AJAX(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            return JsonResponse({"name": "Missing/Incorrect value"}, status=400)
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"email": "Missing/Incorrect value"}, status=400)
        pasword = request.POST.get("password")
        if not pasword:
            return JsonResponse({"password": "Missing/Incorrect value"}, status=400)

        sync_email = request.POST.get("sync_email")
        sync_email = True if sync_email == "true" else False
        person_ads = request.POST.get("person_ads")
        person_ads = True if person_ads == "true" else False
        send_news = request.POST.get("send_news")
        send_news = True if send_news == "true" else False

        kwargs = {
            "name": name,
            "email": email,
            "sync_email": sync_email,
            "person_ads": person_ads,
            "send_news": send_news
        }
        # Password doesnt get logged for security reasons
        logger.debug(f"Processing a new profile with kwargs: {kwargs}")

        profile = helpers.create_new_profile(**kwargs, password=pasword)
        login(request, profile.user, backend="twitter_project.backends.CustomLoginBackend")

        return JsonResponse({})


def get_follow_suggestions_AJAX(request):
    logger.debug("Processing raw request: " + str(request))
    if request.method == "GET":
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        profile = request.user.profile
        limit = request.GET.get("limit")

        if not limit:
            limit = 3
        else:
            try:
                limit = int(limit)
            except ValueError:
                # 400 == bad request
                return HttpResponse(status=400)
            if limit > 20:
                limit = 20

        profiles = helpers.get_follow_suggestions(profile)[:limit]
        context = {"profiles": profiles}
        rendered_template = render(request=request,
                                   template_name="profiles/follow_suggestions.html",
                                   context=context)
        return HttpResponse(rendered_template)

    # 405 == method not allowed
    return HttpResponse(status=405)
