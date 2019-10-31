from django.core.management.base import BaseCommand
from profiles.models import Profile, User, Follow
from faker import Faker
from faker.providers import person, python, date_time, internet
from profiles.helpers import get_username, check_if_user_follows
from random import sample


class Command(BaseCommand):
    help = 'Creates and saves fake profiles using the faker library'

    def add_arguments(self, parser):
        parser.add_argument('num_profiles', type=int)

        parser.add_argument('--follow_all', type=str,
            help="Profile with this username will follow all created Profiles")

    def handle(self, *args, **kwargs):
        num_profiles = kwargs['num_profiles']
        self.stdout.write(f"STEP 1: Create {num_profiles} fake profiles")
        fake = Faker()
        fake.add_provider(person)
        fake.add_provider(python)
        fake.add_provider(date_time)
        fake.add_provider(internet)

        profiles = []
        for _ in range(num_profiles):
            name = fake.name()
            username = get_username(name)
            password = fake.password()

            user = User(username=name, password=password)
            user.save()
            profile = Profile(
                user=user,
                username=username,
                sync_email=fake.pybool(),
                send_news=fake.pybool(),
                personalize_ads=fake.pybool(),
                display_name=fake.user_name(),
                bio=fake.text(),
                location=fake.city(),
                website=fake.domain_name(),
                birth_date=fake.date_between(start_date="-30y", end_date="-16y"),
                verified=fake.pybool(),
                fake=True)
            profile.randomize_media()
            profile.save()
            profiles.append(profile)

        if num_profiles > 1:
            self.stdout.write(f"STEP 2: Create {num_profiles * 10} follows")
            for _ in range(num_profiles * 10):
                follower, following = sample(profiles, k=2)
                if not check_if_user_follows(follower, following):
                    follow = Follow(follower=follower, following=following)
                    follow.save()
        if kwargs['follow_all']:
            follower = Profile.objects.get(username__iexact=kwargs['follow_all'])
            for profile in profiles:
                follow = Follow(follower=follower, following=profile)
                follow.save()

        self.stdout.write("SUCCESS!")
