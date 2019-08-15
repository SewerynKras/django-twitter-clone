from django import forms


class SignUpFormNameEmail:
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)


class SingUpFormCheckboxes:
    sync_email = forms.BooleanField()
    send_news = forms.BooleanField()
    personal_ads = forms.BooleanField()


class SignUpFormNameEmailConfirm:
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)


class SignUpFormCode:
    code = forms.CharField(max_length=8, required=True)


class SignUpFormUsernamePassword:
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.HiddenInput)
