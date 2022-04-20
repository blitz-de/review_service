import factory
from apps.reviews.models import Rater
from faker import Factory as FakerFactory
from django.db.models.signals import post_save

faker = FakerFactory.create()


@factory.django.mute_signals(post_save)
class RaterFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(lambda x: faker.first_name())
    nr_rated_users = factory.LazyAttribute(lambda x: faker.random_int(min=0, max=500))
    is_signed = False
    is_admin = False

    class Meta:
        model = Rater