import json
import logging

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from hypothesis.extra.django import TestCase

from profiles.models import Profile
from tweets import views
from tweets.models import Tweet


class Test_Like_Tweet_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        logging.disable(logging.CRITICAL)

        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            username='test_like_tweet_AJAX', password="secret_hehe_123"
        )
        profile = Profile(user=cls.user, username='like_tweet_test')
        profile.save()
        cls.tweet = Tweet(text="text", author=profile)
        cls.tweet.save()

    def test_incorrect_method(self):
        request = self.factory.get(reverse("tweets:like_tweet"),
                                   {"tweet_id": self.tweet.id})
        response = views.like_tweet_AJAX(request)
        self.assertEqual(response.status_code, 405)

    def test_incorrect_user(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = AnonymousUser()

        response = views.like_tweet_AJAX(request)
        self.assertEqual(response.status_code, 401)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"user": "User not logged in."})

    def test_incorrect_id(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": "..."})
        request.user = self.user

        response = views.like_tweet_AJAX(request)
        self.assertEqual(response.status_code, 403)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"tweet_id": "This tweet doesn't exists."})

    def test_correct_like_add(self):
        likes_before = self.tweet.likes_num

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.like_tweet_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"liked": True})

        likes_now = self.tweet.likes_num
        self.assertEqual(likes_now, likes_before + 1)

    def test_correct_like_remove(self):
        likes_before = self.tweet.likes_num

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.like_tweet_AJAX(request)
        response = views.like_tweet_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"liked": False})

        likes_now = self.tweet.likes_num
        self.assertEqual(likes_now, likes_before)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
