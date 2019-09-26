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


class Test_gifs_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        logging.disable(logging.CRITICAL)

        cls.patcher = patch("tweets.views.helpers.get_giphy", autospec=True)
        cls.mock_get_giphy = cls.patcher.start()

        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            username='test_gif_AJAX', password="secret_hehe_123"
        )
        profile = Profile(user=cls.user, username='get_gif_test')
        profile.save()

    @given(query=st.text(min_size=1),
           offset=st.integers(min_value=0, max_value=20),
           limit=st.integers(min_value=1, max_value=20))
    def test_correct(self, query, offset, limit):

        request = self.factory.get(reverse("tweets:get_gifs"),
                                   {"query": query,
                                    "offset": offset,
                                    "limit": limit})
        response = views.get_gifs_AJAX(request)
        self.assertEqual(response.status_code, 200)

    @given(query=st.text(min_size=1),
           offset=st.one_of(st.integers(max_value=-1),
                            st.integers(min_value=21),
                            st.just("")),
           limit=st.integers(min_value=1, max_value=20))
    def test_wrong_offset(self, query, offset, limit):

        request = self.factory.get(reverse("tweets:get_gifs"),
                                   {"query": query,
                                    "offset": offset,
                                    "limit": limit})
        response = views.get_gifs_AJAX(request)
        self.assertEqual(response.status_code, 400)

    @given(query=st.text(min_size=1),
           offset=st.integers(min_value=0, max_value=20),
           limit=st.one_of(st.integers(max_value=0),
                           st.integers(min_value=21),
                           st.just("")))
    def test_wrong_limit(self, query, offset, limit):
        request = self.factory.get(reverse("tweets:get_gifs"),
                                   {"query": query,
                                    "offset": offset,
                                    "limit": limit})
        response = views.get_gifs_AJAX(request)
        self.assertEqual(response.status_code, 400)

    @given(query=st.just(""),
           offset=st.integers(min_value=0, max_value=20),
           limit=st.integers(min_value=1, max_value=20))
    def test_wrong_query(self, query, offset, limit):
        request = self.factory.get(reverse("tweets:get_gifs"),
                                   {"query": query,
                                    "offset": offset,
                                    "limit": limit})
        response = views.get_gifs_AJAX(request)
        self.assertEqual(response.status_code, 400)

    @given(query=st.text(min_size=1),
           offset=st.integers(min_value=0, max_value=20),
           limit=st.integers(min_value=1, max_value=20))
    def test_wrong_method(self, query, offset, limit):
        request = self.factory.post(reverse("tweets:get_gifs"),
                                    {"query": query,
                                     "offset": offset,
                                     "limit": limit})
        response = views.get_gifs_AJAX(request)
        self.assertEqual(response.status_code, 400)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
        cls.patcher.stop()


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
        self.assertEqual(cont, {"retweet": "Incorrect retweet id"})

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
           ch4=st.text(max_size=25))
    def test_correct_poll(self, ch1, ch2, ch3, ch4):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                        "media": {
                                        "type": "poll",
                                        "values": {
                                            "choice1_text": ch1,
                                            "choice2_text": ch2,
                                            "choice3_text": ch3,
                                            "choice4_text": ch4,
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
           ch4=st.text(min_size=26))
    def test_incorrect_poll(self, ch1, ch2, ch3, ch4):
        request = self.factory.post(reverse("tweets:new_tweet"),
                                    {"text": 'sometext',
                                     "media": {
                                     "type": "poll",
                                     "values": {
                                            "choice1_text": ch1,
                                            "choice2_text": ch2,
                                            "choice3_text": ch3,
                                            "choice4_text": ch4,
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
        cls.patcher.stop()


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
        likes_before = self.tweet.likes

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.like_tweet_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"liked": True})

        likes_now = self.tweet.likes
        self.assertEqual(likes_now, likes_before + 1)

    def test_correct_like_remove(self):
        likes_before = self.tweet.likes

        request = self.factory.post(reverse("tweets:like_tweet"),
                                    {"tweet_id": self.tweet.id})
        request.user = self.user

        response = views.like_tweet_AJAX(request)
        response = views.like_tweet_AJAX(request)

        self.assertEqual(response.status_code, 200)
        cont = json.loads(response.content)
        self.assertEqual(cont, {"liked": False})

        likes_now = self.tweet.likes
        self.assertEqual(likes_now, likes_before)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
