from django.core.management.base import BaseCommand
from profiles.models import Profile


class Command(BaseCommand):
    help = 'Deletes all profiles created using create-fake-profiles'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting all fake profiles")
        profiles = Profile.objects.filter(fake=True)
        profiles.delete()
        self.stdout.write("SUCCESS!")
