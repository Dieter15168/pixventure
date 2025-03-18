import pytest
import django
from django.conf import settings
from .factories import UserFactory, MediaItemFactory, TermFactory

@pytest.fixture
def user_factory():
    """
    Returns the UserFactory class. 
    You can call user_factory() to create a User, 
    or user_factory(username="alice") to override fields.
    """
    return UserFactory

@pytest.fixture
def media_item_factory():
    """
    Returns the MediaItemFactory class.
    """
    return MediaItemFactory

@pytest.fixture
def term_factory():
    """
    Returns the TermFactory class.
    """
    return TermFactory