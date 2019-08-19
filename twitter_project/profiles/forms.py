from django import forms
from profiles import models


class SignUpForm(forms.ModelForm):
    name_first = forms.CharField(required=True)
    name_verify = forms.CharField(required=True)
    email_first = forms.EmailField(required=True)
    email_verify = forms.EmailField(required=True)
    code = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = models.Profile
        fields = ['sync_email', 'send_news', 'personalize_ads']
