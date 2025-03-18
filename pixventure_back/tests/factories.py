# tests/factories.py
import factory
from django.contrib.auth.models import User
from media.models import MediaItem
from taxonomy.models import Term

class UserFactory(factory.django.DjangoModelFactory):
    """
    Creates a Django User with a unique username and
    default password of 'testpass'.
    """
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass")


class MediaItemFactory(factory.django.DjangoModelFactory):
    """
    Creates a MediaItem. Defaults to a PHOTO type with pending moderation status.
    """
    class Meta:
        model = MediaItem

    media_type = MediaItem.PHOTO
    status = MediaItem.PENDING_MODERATION
    owner = factory.SubFactory(UserFactory)  # By default, create a user

    original_filename = factory.Sequence(lambda n: f"image_{n}.jpg")


class TermFactory(factory.django.DjangoModelFactory):
    """
    Creates a Term. Defaults to a TAG, but you can override term_type=Term.CATEGORY in tests.
    """
    class Meta:
        model = Term

    term_type = Term.TAG
    name = factory.Sequence(lambda n: f"Term{n}")
    slug = factory.Sequence(lambda n: f"term-{n}")
