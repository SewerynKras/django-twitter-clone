import logging

from django.contrib.auth.models import User
from hypothesis.extra.django import TestCase

from profiles.helpers import get_username
from profiles.models import Profile


class Test_get_username(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.disable(logging.CRITICAL)

    def test_correct_name_once(self):
        name = "n a me123"

        new_name = get_username(name)
        self.assertEqual("name", new_name)

    def test_correct_name_multiple(self):
        name = "name"

        new_name1 = get_username(name)
        user = User.objects.create_user(username=new_name1,
                                        password="secret123")
        user.save()
        profile = Profile(user=user, username=new_name1)
        profile.save()

        new_name2 = get_username(name)
        user = User.objects.create_user(username=new_name2,
                                        password="secret123")
        user.save()
        profile = Profile(user=user, username=new_name2)
        profile.save()

        new_name3 = get_username(name)
        user = User.objects.create_user(username=new_name3,
                                        password="secret123")
        user.save()
        profile = Profile(user=user, username=new_name3)
        profile.save()

        self.assertEqual("name", new_name1)
        self.assertEqual("name1", new_name2)
        self.assertEqual("name2", new_name3)

    def test_incorrect_name_forbidden(self):
        name = "home"

        new_name = get_username(name)

        self.assertEqual("home1", new_name)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
