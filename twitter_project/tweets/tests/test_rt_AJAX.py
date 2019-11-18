import json
import logging

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from hypothesis.extra.django import TestCase

from profiles.models import Profile
from tweets import views
from tweets.models import Tweet


class Test_RT_Tweet_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        logging.disable(logging.CRITICAL)

        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            username='test_rt_tweet_AJAX', password="secret_hehe_123"
        )
        profile = Profile(user=cls.user, username='rt_tweet_test')
        profile.save()
        cls.tweet = Tweet(text="text", author=profile)
        cls.tweet.save()

    def test_incorrect_method(self):
        request = self.factory.get(reverse("tweets:rt"),
                                   {"tweet_id": self.tweet.id})
        response = views.rt_AJAX(request)
        self.assertEqual(response.status_code, 405)

    def test_incorrect_user(self):
        request = self.factory.post(reverse("tweets:rt"),
                                    {"tweet_id": self.tweet.id})
        request.user = AnonymousUser()

        response = views.rt_AJAX(request)
        self.assertEqual(response.status_code, 401)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"user": "User not logged in."})

    def test_incorrect_id(self):
        request = self.factory.post(reverse("tweets:rt"),
                                    {"tweet_id": "..."})
        request.user = self.user

        response = views.rt_AJAX(request)
        self.assertEqual(response.status_code, 404)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"tweet_id": "This tweet doesn't exists."})

    def test_correct_rt(self):
        rts_before = self.tweet.retweets_num

        request = self.factory.post(reverse("tweets:rt"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.rt_AJAX(request)

        self.assertEqual(response.status_code, 200)

        rts_now = self.tweet.retweets_num
        self.assertEqual(rts_now, rts_before + 1)

    def test_incorrect_rt_multiple(self):
        rts_before = self.tweet.retweets_num

        request = self.factory.post(reverse("tweets:rt"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.rt_AJAX(request)
        response = views.rt_AJAX(request)

        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"tweet_id": "You cannot retweet the same tweet multiple times."})

        rts_now = self.tweet.retweets_num
        self.assertEqual(rts_now, rts_before + 1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
