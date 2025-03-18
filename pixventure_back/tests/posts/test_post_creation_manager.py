# tests/test_post_creation_manager.py

import pytest
from django.contrib.auth import get_user_model
from posts.models import Post, PostMedia
from taxonomy.models import Term
from media.models import MediaItem
from posts.managers.post_creation_manager import PostCreationManager

User = get_user_model()

@pytest.mark.django_db
class TestPostCreationManager:

    def test_create_post_valid_data(self, user_factory, media_item_factory, term_factory):
        user = user_factory()  # create a user
        media1 = media_item_factory(owner=user)
        media2 = media_item_factory(owner=user)
        cat_term = term_factory(term_type=Term.CATEGORY)
        tag_term = term_factory(term_type=Term.TAG)

        data = {
            "name": "My Test Post",
            "featured_item": media1.id,
            "items": [media1.id, media2.id],
            "terms": [cat_term.id, tag_term.id],
            "text": "Hello world",
        }

        post = PostCreationManager.create_post(data, user)

        assert post.pk is not None
        assert post.owner == user
        assert post.name == "My Test Post"
        assert post.slug  # slug is generated
        assert post.featured_item == media1
        assert post.terms.count() == 2  # category + tag
        assert PostMedia.objects.filter(post=post).count() == 2

    def test_create_post_skip_invalid_terms(self, user_factory, media_item_factory, term_factory):
        user = user_factory()
        valid_cat = term_factory(term_type=Term.CATEGORY)
        media = media_item_factory(owner=user)

        data = {
            "name": "Post With Invalid Terms",
            "featured_item": None,
            "items": [media.id],
            "terms": [999, valid_cat.id, 1000],  # 999 and 1000 presumably invalid
            "text": "Some text"
        }

        post = PostCreationManager.create_post(data, user)

        assert post.pk is not None
        # Terms should only contain the valid category
        assert list(post.terms.values_list('id', flat=True)) == [valid_cat.id]

    def test_create_post_no_categories_at_all(self, user_factory, media_item_factory):
        user = user_factory()
        media = media_item_factory(owner=user)

        data = {
            "name": "No Categories In DB",
            "featured_item": None,
            "items": [media.id],
            "terms": [],  # no terms
            "text": "No categories in system"
        }

        post = PostCreationManager.create_post(data, user)
        assert post.pk is not None
        # If there's truly no category in the database, main_category should be None
        assert post.main_category is None
        assert post.terms.count() == 0

    def test_create_post_raises_on_invalid_media(self, user_factory, media_item_factory):
        user = user_factory()
        # Create a media item for a different user so it fails
        other_user = user_factory()
        alien_media = media_item_factory(owner=other_user)

        data = {
            "name": "Should Fail",
            "featured_item": None,
            "items": [alien_media.id],
            "terms": [],
            "text": ""
        }

        with pytest.raises(ValueError) as exc:
            PostCreationManager.create_post(data, user)

        assert "One or more media items do not exist or do not belong to you." in str(exc.value)
