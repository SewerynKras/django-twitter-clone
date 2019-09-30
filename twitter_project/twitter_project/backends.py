from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from twitter_project import helpers
from django.conf import settings


class CustomLoginBackend:
    """
    Authenticate using an email address, phone number or username
    """

    def authenticate(self, request, identifier, password):
        if helpers.is_valid_email(identifier):
            get_kwargs = {"email": identifier}
            error = settings.INVALID_EMAIL_MESSAGE
        elif helpers.is_valid_phonenumber(identifier):
            get_kwargs = {"profile__phone": identifier}
            error = settings.INVALID_PHONE_MESSAGE
        else:
            get_kwargs = {"username": identifier}
            error = settings.INVALID_USERNAME_MESSAGE

        try:
            user = User.objects.get(**get_kwargs)
            if not user.check_password(password):
                raise ObjectDoesNotExist
            return user
        except (TypeError, ObjectDoesNotExist, ValueError):
            raise ObjectDoesNotExist(error)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
