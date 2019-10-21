import json
import logging
from datetime import timedelta

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from hypothesis.extra.django import TestCase

from profiles.models import Profile
from tweets import views
from tweets.models import Media, Poll, Tweet


class Test_choose_poll_option_AJAX(TestCase):

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
        tweet = Tweet(text="text", author=profile)
        tweet.save()
        cls.tweet = tweet
        poll = Poll(choice1_text="1",
                    choice2_text="2",
                    choice3_text="3",
                    choice4_text="4")
        poll.end_date = timezone.now() + timedelta(seconds=1000)
        poll.save()
        cls.poll = poll
        media = Media(type="poll", poll=poll, tweet=tweet)
        media.save()

        tweet_exp = Tweet(text="text exp", author=profile)
        tweet_exp.save()
        cls.tweet_exp = tweet_exp
        poll_exp = Poll(choice1_text="1",
                        choice2_text="2",
                        choice3_text="3",
                        choice4_text="4")
        poll_exp.end_date = timezone.now() - timedelta(seconds=2)
        poll_exp.save()
        cls.poll_exp = poll_exp
        media_exp = Media(type="poll", poll=poll_exp, tweet=tweet_exp)
        media_exp.save()

    def test_incorrect_method(self):
        request = self.factory.get(reverse("tweets:like_tweet"),
                                   {"tweet_id": self.tweet.id,
                                    "choice": 1})
        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 405)

    def test_incorrect_user(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 1})
        request.user = AnonymousUser()

        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 401)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"user": "User not logged in."})

    def test_incorrect_id(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": "...",
                                    "choice": 1})
        request.user = self.user

        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 403)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"tweet_id": "This tweet doesn't exists."})

    def test_incorrect_choice(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 5})
        request.user = self.user

        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 403)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"choice": "Invalid choice."})

    def test_correct_choice_just_add(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 1})
        request.user = self.user

        votes_before = self.poll.votes1

        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"voted": "1"})
        votes_after = self.poll.votes1
        self.assertEqual(votes_before + 1, votes_after)

    def test_correct_choice_add_remove(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 1})
        request.user = self.user

        votes_before = self.poll.votes1

        response = views.choose_poll_option_AJAX(request)

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user
        response = views.choose_poll_option_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"voted": None})
        votes_after = self.poll.votes1
        self.assertEqual(votes_before, votes_after)

    def test_correct_choice_change(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 1})
        request.user = self.user

        votes_before1 = self.poll.votes1
        votes_before2 = self.poll.votes2

        response = views.choose_poll_option_AJAX(request)

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id,
                                    "choice": 2})
        request.user = self.user
        response = views.choose_poll_option_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"voted": "2"})
        votes_after1 = self.poll.votes1
        votes_after2 = self.poll.votes2
        self.assertEqual(votes_before1, votes_after1)
        self.assertEqual(votes_before2 + 1, votes_after2)

    def test_incorrect_expired(self):
        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet_exp.id,
                                    "choice": 1})
        request.user = self.user

        response = views.choose_poll_option_AJAX(request)
        self.assertEqual(response.status_code, 410)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
