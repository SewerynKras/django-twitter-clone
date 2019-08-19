import re
from profiles.models import Profile, User
from django.db.models.functions import Lower


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

    # get all usernames that start with $name
    pattern = fr'^{name}\d*'
    usernames = Profile.objects.filter(username__iregex=pattern).order_by(Lower("username"))

    # in case the name is unique
    if len(usernames) == 0:
        return name

    # get the number
    number = usernames.last().username[len(name):]

    if number == "":
        return name + "1"
    else:
        number = int(number)
        number += 1
        return name + str(number)


def is_email_valid(email):
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(pattern, email)


def is_email_unique(email):
    return not User.objects.filter(email__iexact=email).exists()
