from django.core.management.base import BaseCommand
from tweets.models import Tweet


class Command(BaseCommand):
    help = 'Deletes all tweets created using create-fake-tweets'

    def handle(self, *args, **kwargs):
        self.stdout.write(f"Deleting fake tweets")

        fake_tweets = Tweet.objects.filter(author__fake=True)
        fake_tweets.delete()
        self.stdout.write("SUCCESS!")
