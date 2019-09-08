from django.core.management.base import BaseCommand
from django.conf import settings
from tweets.models import Gif_Category
from tweets.helpers import download_gif
import urllib.request
import urllib.parse
import json


class Command(BaseCommand):
    help = 'Downloads preview thumbnails for each default gif category'

    def handle(self, *args, **kwargs):
        # purge all previous entries
        for gif_cat in Gif_Category.objects.all():
            gif_cat.delete()

        URL_BASE = ("https://api.giphy.com/v1/gifs/search?"
                    "api_key={key}&"
                    "q={name}&"
                    "limit=1&offset=0&rating=PG-13&lang=en")
        MESS_BASE = "Name: {name}\t|\tStatus: {status}\t|\t{message}"

        for name in settings.DEFAULT_GIFS:
            safe_name = urllib.parse.quote(name)
            try:
                data = urllib.request.urlopen(URL_BASE.format(
                                              key=settings.GIPHY_API_KEY,
                                              name=safe_name)).read()
            except:
                self.stdout.write(self.style.ERROR(
                    MESS_BASE.format(name=name,
                                     status="ERROR",
                                     message="NETWORK ERROR")))
                continue
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(
                    MESS_BASE.format(name=name,
                                     status="ERROR",
                                     message="DECODE ERROR (no value?)")))
                continue
            status = data['meta']['msg']
            if status != "OK":
                self.stdout.write(self.style.ERROR(
                    MESS_BASE.format(name=name,
                                     status="ERROR",
                                     message=f"RESPONSE STATUS: {status}")))
                continue
            try:
                gif = download_gif(data['data'][0])
                gif.save()
                category = Gif_Category(category_name=name, gif=gif)
                category.save()
            except:
                self.stdout.write(self.style.ERROR(
                    MESS_BASE.format(name=name,
                                     status="ERROR",
                                     message="MODEL CREATE ERROR")))
                continue

            self.stdout.write(self.style.SUCCESS(
                MESS_BASE.format(name=name,
                                 status="SUCCESS",
                                 message="")))
