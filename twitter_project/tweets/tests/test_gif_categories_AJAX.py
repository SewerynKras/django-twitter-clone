import logging

from django.urls import reverse
from django.test import RequestFactory
from hypothesis.extra.django import TestCase

from tweets import views


class Test_GIF_Categories_Tweet_AJAX(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        logging.disable(logging.CRITICAL)

    def test_incorrect_method(self):
        request = self.factory.post(reverse("tweets:get_gif_categories"))
        response = views.get_gif_categories_AJAX(request)
        self.assertEqual(response.status_code, 405)

    def test_correct(self):
        request = self.factory.get(reverse("tweets:get_gif_categories"))
        response = views.get_gif_categories_AJAX(request)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
