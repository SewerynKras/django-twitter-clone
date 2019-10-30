from django.core.management.base import BaseCommand
from profiles.models import Profile
from tweets.models import Tweet, Images, Gif, Media, Poll, PollVote, Like
from faker import Faker
from random import choice, sample, randint
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Creates and saves fake profiles using the faker library'

    def add_arguments(self, parser):
        parser.add_argument('num_tweets', type=int)

    def handle(self, *args, **kwargs):
        num_tweets = kwargs['num_tweets']
        self.stdout.write(f"STEP 1: Create {num_tweets} fake tweets")

        fake_profiles = [i for i in Profile.objects.filter(fake=True)]
        if len(fake_profiles) == 0:
            self.stdout.write("No fake profiles found! Create some first using create-fake-profiles")
            self.stdout.write("Aborting!")
            return

        fake = Faker()

        tweets = []
        gifs = Gif.objects.all()
        for _ in range(num_tweets):
            author = choice(fake_profiles)
            text = fake.text()[:256]
            tweet = Tweet(author=author, text=text)

            media = None

            # 1/3 chance to have media
            if randint(1, 3) == 1:
                media = Media()

                # type
                m_type = randint(1, 3)
                if m_type == 1:
                    # GIF
                    gif = gifs[randint(0, len(gifs) - 1)]
                    gif.pk = None
                    gif.save()
                    media.type = "gif"
                    media.gif = gif
                elif m_type == 2:
                    # IMAGE
                    # I downloaded some random stock images and put them
                    # in media/tweet_images/dummy_images/
                    img_num = randint(1, 4)
                    imgs = sample(range(15), img_num)
                    img = Images()
                    for i in range(img_num):
                        setattr(img, f"image_{i+1}",
                                f"tweet_images/dummy_images/{imgs[i]}.jpg")
                    img.save()
                    media.type = "img"
                    media.img = img
                else:
                    # POLL
                    poll = Poll()
                    options = randint(2, 4)
                    for i in range(1, options+1):
                        setattr(poll, f"choice{i}_text", fake.word())

                    sec_left = randint(1, 1000)
                    poll.end_date = timezone.now() + timedelta(seconds=sec_left)
                    poll.save()

                    votes = randint(1, max(1, len(fake_profiles)//4))
                    vote_profiles = sample(fake_profiles, k=votes)
                    for i in range(votes):
                        chosen = randint(1, options)
                        vote = PollVote(poll=poll, choice=chosen, author=vote_profiles[i])
                        vote.save()
                    media.type = "poll"
                    media.poll = poll

            roll = randint(1, 6)
            # 1/6 chance to be a retweet
            if tweets and roll == 1:
                tweet.retweet_to = choice(tweets)
            # 1/6 chance to be a comment
            elif tweets and roll == 2:
                tweet.comment_to = choice(tweets)

            tweet.save()
            tweets.append(tweet)

            num_likes = randint(0, max(1, len(fake_profiles)//4))
            like_prof = sample(fake_profiles, k=num_likes)
            for i in range(num_likes):
                like = Like(author=like_prof[i], tweet=tweet)
                like.save()

            if media:
                media.tweet = tweet
                media.save()
        self.stdout.write("SUCCESS!")
