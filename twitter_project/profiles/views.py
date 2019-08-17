from django.views.generic import DetailView, TemplateView
from profiles import models, forms
from django.contrib.auth.models import User
from django.shortcuts import redirect


class ProfileView(DetailView):
    model = models.Profile
    template_name = "profiles/profile.html"
    context_object_name = 'profile'


class SignupView(TemplateView):
    template_name = "profiles/sign_up.html"

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
