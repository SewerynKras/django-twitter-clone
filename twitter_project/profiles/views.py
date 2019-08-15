from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from profiles import models, forms


class ProfileView(DetailView):
    model = models.Profile
    template_name = "profiles/profile.html"
    context_object_name = 'profile'


class SignupView(TemplateView):
    template_name = "profiles/sign_up.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["part_1_form"] = "PART 1"
        #context["part_1_form"] = forms.SignUpFormNameEmail
        context["part_2_form"] = forms.SingUpFormCheckboxes
        context["part_3_form"] = forms.SignUpFormNameEmailConfirm
        context["part_4_form"] = forms.SignUpFormCode
        context["part_5_form"] = forms.SignUpFormUsernamePassword
        return context
