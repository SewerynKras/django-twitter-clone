from django.views.generic import TemplateView
from profiles import models, forms, helpers
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from twitter_project.logging import logger
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ObjectDoesNotExist
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

    def post(self, request):
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            user = User(name=form.cleaned_data['name_verify'])
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile.user = user
            profile.save()
            redirect("/")


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

        login(request, user)
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

        login(request, user)
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
        profile = models.Profile.objects.get(username__iexact=profile_id)
        context = {"profile": profile}
        rendered_template = render(request=request,
                                   template_name="profiles/profile.html",
                                   context=context)
        return HttpResponse(rendered_template)
