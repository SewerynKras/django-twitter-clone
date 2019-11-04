import re
from profiles.models import Profile, User, Follow
from django.db.models.functions import Lower
from twitter_project.logging import logger
from django.conf import settings


def get_username(name):
    """Generates a unique username based on the given name
    The username will contain both parts of the name and a
    number at the end if the name is already taken

    for example:
        get_username("Seweryn Kras") -> "SewerynKras"
        get_username("Seweryn Kras") -> "SewerynKras1"
        get_username("Seweryn Kras") -> "SewerynKras2"
    """
    # clean the name of all non letters
    pattern = r'[^a-zA-Z]+'
    name = re.sub(pattern, "", name)

    if name.lower() not in settings.FORBIDDEN_NAMES:
        # get all usernames that start with $name
        pattern = fr'^{name}\d*'
        usernames = Profile.objects.filter(username__iregex=pattern).order_by(Lower("username"))

        # in case the name is unique and not forbidden
        if not usernames.exists():
            logger.debug(f"Name: {name} is valid")
            return name
        # get the number
        number = usernames.last().username[len(name):]
    else:
        number = ""

    if number == "":
        number = 1
    else:
        number = int(number)
        number += 1
    new_name = name + str(number)

    logger.debug(f"Name: {name} is not valid so the new username is {new_name}")
    return new_name


def get_single_author(id):
    """
    Queries an author with the given id.

    Arguments:
        id {str}

    Returns:
        Profile
    """
    return Profile.objects.get(username__iexact=id)


def is_email_valid(email):
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    matches = bool(re.match(pattern, email))
    logger.debug(f"Validating email: {email} verdict: {matches}")
    return matches


def is_email_unique(email):
    unique = not User.objects.filter(email__iexact=email).exists()
    logger.debug(f"Checking if email: {email} is unique, verdict: {unique}")
    return unique


def check_if_user_follows(follower, following):
    """
    Returns a boolean value describing wheather a Follow objects exists
    between the follower and following

    Arguments:
        follower {Profile}
        following {Profile}

    Returns:
        bool
    """
    return Follow.objects.filter(follower=follower, following=following).exists()


def create_new_profile(name, email, password, sync_email, person_ads, send_news):
    """
    Registers a new user by creating and saving a User and Profile instance

    Arguments:
        name {str}
        email {str}
        password {str}
        sync_email {bool}
        person_ads {bool}
        send_news {bool}

    Returns:
        Profile
    """
    username = get_username(name)
    user = User(username=email, email=email)
    user.set_password(password)
    user.save()
    profile = Profile(user=user,
                      username=username,
                      sync_email=sync_email,
                      send_news=send_news,
                      personalize_ads=person_ads,
                      display_name=name)
    profile.randomize_media()
    profile.save()
    return profile
