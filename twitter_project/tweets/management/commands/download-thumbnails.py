from django.core.management.base import BaseCommand
from django.conf import settings
import urllib.request
import urllib.parse
import json


class Command(BaseCommand):
    help = 'Downloads preview thumbnails for each default gif category'

    def handle(self, *args, **kwargs):
        URL_BASE = ("https://api.giphy.com/v1/gifs/search?"
                    "api_key={key}&"
                    "q={name}&"
                    "limit=1&offset=0&rating=PG-13&lang=en")
        MESS_BASE = "Name: {name}\t|\tStatus: {status}\t|\t {message}"

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
                with open(settings.MEDIA_ROOT + "\\gif_thumbnails\\" + name + ".gif", "wb") as f:
                    f.write(urllib.request.urlopen(
                        data['data'][0]['images']['original_still']['url']).read())
            except:
                self.stdout.write(self.style.ERROR(
                    MESS_BASE.format(name=name,
                                     status="ERROR",
                                     message="FILE WRITE ERROR")))
                continue
            self.stdout.write(self.style.SUCCESS(
                MESS_BASE.format(name=name,
                                 status="SUCCESS",
                                 message="")))
