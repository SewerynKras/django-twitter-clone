from django import forms
from profiles import models


class SignUpForm(forms.ModelForm):
    name = forms.CharField(required=True, max_length=50)
    email = forms.EmailField(required=True)
    code = forms.CharField(required=True, max_length=4)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = models.Profile
        fields = ['sync_email', 'send_news', 'personalize_ads']


class LoginForm(forms.Form):
    identifier = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Phone, email or username',
               'id': 'loginform-id'}),
               label='')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password',
               'id': 'loginform-password'}),
               label='')
