import json
import logging
import re
from unittest.mock import PropertyMock, patch

import hypothesis.strategies as st
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from hypothesis import assume, given
from hypothesis.extra.django import TestCase

from profiles.models import Profile
from tweets import views
from tweets.models import Tweet


class Test_new_tweet_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        logging.disable(logging.CRITICAL)
        cls.patcher = patch("tweets.views.helpers.parse_new_tweet")
        cls.mock_new_tweet = cls.patcher.start()
        type(cls.mock_new_tweet.return_value).id = PropertyMock(return_value="5")

        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            username='test_new_tweet_AJAX', password="secret_hehe_123"
        )
        profile = Profile(user=cls.user, username='new_tweet_test')
        profile.save()
        retweet = Tweet(text="text", author=profile)
        retweet.save()
        cls.retweet_id = retweet.id

    def test_no_author(self):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext'})
        request.user = AnonymousUser()

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 401)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"user": "User not logged in."})

    @given(text=st.text(min_size=1, max_size=255))
    def test_correct_text_only(self, text):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": text},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertIn("id", cont.keys())

    def test_incorrect_retweet(self):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                     "retweet_id": ".."},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"retweet": "Incorrect retweet id."})

    def test_correct_retweet(self):

        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                    "retweet_id": self.retweet_id},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertIn("id", cont.keys())

    @given(text=st.one_of(st.just(""),
                          st.text(min_size=265, max_size=500)))
    def test_incorrect_text_only(self, text):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": text},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("text", cont.keys())

    @given(mt=st.one_of(st.just(""),
                        st.text(max_size=20)))
    def test_incorrect_media_type(self, mt):
        assume(mt not in ['img', 'gif', 'poll'])
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                        "media": {
                                           "type": mt,
                                           "values": {
                                           }
                                        }
                                    },
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("media", cont.keys())

    def test_incorrect_media_values(self):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                        "media": {
                                           "type": "img",
                                           "values": []
                                        }
                                    },
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("values", cont.keys())

    @given(img1=st.from_regex(r'data:image/([a-zA-Z]+);base64,([^":]+)', fullmatch=True),
           img2=st.from_regex(r'data:image/([a-zA-Z]+);base64,([^":]+)', fullmatch=True),
           img3=st.from_regex(r'data:image/([a-zA-Z]+);base64,([^":]+)', fullmatch=True),
           img4=st.from_regex(r'data:image/([a-zA-Z]+);base64,([^":]+)', fullmatch=True))
    def test_correct_images(self, img1, img2, img3, img4):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                    "media": {
                                        "type": "img",
                                        "values": {
                                            "image_1": img1,
                                            "image_2": img2,
                                            "image_3": img3,
                                            "image_4": img4,
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertIn("id", cont.keys())

    @given(img1=st.text(min_size=1),
           img2=st.text(min_size=1),
           img3=st.text(min_size=1),
           img4=st.text(min_size=1))
    def test_incorrect_images(self, img1, img2, img3, img4):
        assume(not re.match(r'data:image/([a-zA-Z]+);base64,([^":]+)', img1))
        assume(not re.match(r'data:image/([a-zA-Z]+);base64,([^":]+)', img2))
        assume(not re.match(r'data:image/([a-zA-Z]+);base64,([^":]+)', img3))
        assume(not re.match(r'data:image/([a-zA-Z]+);base64,([^":]+)', img4))

        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                    "media": {
                                        "type": "img",
                                        "values": {
                                            "image_1": img1,
                                            "image_2": img2,
                                            "image_3": img3,
                                            "image_4": img4,
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("image_1", cont.keys())
        self.assertIn("image_2", cont.keys())
        self.assertIn("image_3", cont.keys())
        self.assertIn("image_4", cont.keys())

    @given(url=st.from_regex(r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+', fullmatch=True),
           thb=st.from_regex(r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+', fullmatch=True))
    def test_correct_gif(self, url, thb):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                    "media": {
                                        "type": "gif",
                                        "values": {
                                            "gif_url": url,
                                            "thumb_url": thb
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertIn("id", cont.keys())

    @given(url=st.text(),
           thb=st.text())
    def test_incorrect_gif(self, url, thb):
        assume(not re.match(r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+', url))
        assume(not re.match(r'https://media[0-9]*\.giphy\.com/media/[\w#!:.?+=&%@!\-/]+', thb))
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                    "media": {
                                        "type": "gif",
                                        "values": {
                                            "gif_url": url,
                                            "thumb_url": thb
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("values", cont.keys())

    @given(ch1=st.text(max_size=25),
           ch2=st.text(max_size=25),
           ch3=st.text(max_size=25),
           ch4=st.text(max_size=25),
           days=st.integers(min_value=0, max_value=7),
           hours=st.integers(min_value=0, max_value=23),
           minutes=st.integers(min_value=0, max_value=59))
    def test_correct_poll(self, ch1, ch2, ch3, ch4, days, hours, minutes):
        assume(days + hours + minutes != 0)
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                        "media": {
                                        "type": "poll",
                                        "values": {
                                            "choice1_text": ch1,
                                            "choice2_text": ch2,
                                            "choice3_text": ch3,
                                            "choice4_text": ch4,
                                            "days_left": days,
                                            "hours_left": hours,
                                            "minutes_left": minutes
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertIn("id", cont.keys())

    @given(ch1=st.text(min_size=26),
           ch2=st.text(min_size=26),
           ch3=st.text(min_size=26),
           ch4=st.text(min_size=26),
           days=st.integers(min_value=0, max_value=7),
           hours=st.integers(min_value=0, max_value=23),
           minutes=st.integers(min_value=0, max_value=59))
    def test_incorrect_poll_text(self, ch1, ch2, ch3, ch4, days, hours, minutes):
        assume(days + hours + minutes != 0)
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                     "media": {
                                     "type": "poll",
                                     "values": {
                                            "choice1_text": ch1,
                                            "choice2_text": ch2,
                                            "choice3_text": ch3,
                                            "choice4_text": ch4,
                                            "days_left": days,
                                            "hours_left": hours,
                                            "minutes_left": minutes
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("choice1_text", cont.keys())
        self.assertIn("choice2_text", cont.keys())
        self.assertIn("choice3_text", cont.keys())
        self.assertIn("choice4_text", cont.keys())

    @given(ch1=st.text(max_size=25),
           ch2=st.text(max_size=25),
           ch3=st.text(max_size=25),
           ch4=st.text(max_size=25),
           days=st.one_of(st.integers(max_value=-1), st.integers(min_value=8)),
           hours=st.one_of(st.integers(max_value=-1), st.integers(min_value=24)),
           minutes=st.one_of(st.integers(max_value=-1), st.integers(min_value=60)))
    def test_incorrect_poll_time(self, ch1, ch2, ch3, ch4, days, hours, minutes):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                     "media": {
                                     "type": "poll",
                                     "values": {
                                            "choice1_text": ch1,
                                            "choice2_text": ch2,
                                            "choice3_text": ch3,
                                            "choice4_text": ch4,
                                            "days_left": days,
                                            "hours_left": hours,
                                            "minutes_left": minutes
                                        }
                                    }},
                                    content_type="application/json")
        request.user = self.user

        response = views.new_tweet_AJAX(request)
        self.assertEqual(response.status_code, 400)
        cont = json.loads(response.content)
        self.assertIn("days_left", cont.keys())
        self.assertIn("hours_left", cont.keys())
        self.assertIn("minutes_left", cont.keys())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
        cls.patcher.stop()
