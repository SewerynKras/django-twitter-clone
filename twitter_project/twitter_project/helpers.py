import re
import phonenumbers as pn
from phonenumbers.phonenumberutil import NumberParseException


def is_valid_email(text):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.match(pattern, text)


def is_valid_phonenumber(text):
    try:
        num = pn.parse(text, None)
    except NumberParseException:
        return False

    return pn.is_possible_number(num) and pn.is_valid_number(num)
