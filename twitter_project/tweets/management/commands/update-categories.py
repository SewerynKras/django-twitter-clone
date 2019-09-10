from django.core.management.base import BaseCommand
from django.conf import settings
from tweets.models import Gif_Category
from tweets.helpers import get_giphy


class Command(BaseCommand):
    help = 'Downloads preview thumbnails for each default gif category'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting previous categories")
        # purge all previous entries
        for gif_cat in Gif_Category.objects.all():
            gif_cat.delete()

        MESS_BASE = "Name: {name}\t|\tStatus: {status}\t|\t{message}"

        for name in settings.DEFAULT_GIFS:
            try:
                gif = get_giphy(query=name, limit=1, offset=1)[0]
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
