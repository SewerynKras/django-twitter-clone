from django.test import RequestFactory
from django.urls import reverse
from unittest.mock import patch
from tweets import views
from django.contrib.auth.models import User
from profiles.models import Profile

from hypothesis import given
from hypothesis.extra.django import TestCase
import hypothesis.strategies as st


class Test_gifs_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(
            username='test_gif_AJAX', password="secret_hehe_123"
        )
        profile = Profile(user=cls.user, username='test123')
        profile.save()

    @given(query=st.text(min_size=1),
           offset=st.integers(min_value=0, max_value=20),
           limit=st.integers(min_value=1, max_value=20))
    def test_correct(self, query, offset, limit):

        with patch("tweets.views.helpers.get_giphy", autospec=True):
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

        with patch("tweets.views.helpers.get_giphy", autospec=True):
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
        with patch("tweets.views.helpers.get_giphy", autospec=True):
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
        with patch("tweets.views.helpers.get_giphy", autospec=True):
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
        with patch("tweets.views.helpers.get_giphy", autospec=True):
            request = self.factory.post(reverse("tweets:get_gifs"),
                                        {"query": query,
                                         "offset": offset,
                                         "limit": limit})
            response = views.get_gifs_AJAX(request)
            self.assertEqual(response.status_code, 400)
