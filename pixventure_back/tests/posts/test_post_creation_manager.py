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

        assert post.pk is not None, "Post creation failed: post.pk is None"
        assert post.owner == user, f"Post owner mismatch: expected {user}, got {post.owner}"
        assert post.name == "My Test Post", f"Post name mismatch: expected 'My Test Post', got '{post.name}'"
        assert post.slug, "Post slug was not generated"
        assert post.featured_item == media1, f"Post featured_item mismatch: expected {media1}, got {post.featured_item}"
        assert post.terms.count() == 2, f"Expected 2 terms, got {post.terms.count()}"
        assert PostMedia.objects.filter(post=post).count() == 2, (
            f"Expected 2 media items, got {PostMedia.objects.filter(post=post).count()}"
        )

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

    def test_create_post_no_categories_at_all(self, user_factory, media_item_factory, term_factory):
        user = user_factory()
        media = media_item_factory(owner=user)

        # Create a fallback category in the DB, so the manager can pick it up
        fallback_cat = term_factory(
            term_type=Term.CATEGORY, 
            name="Default Fallback Category", 
            slug="default-fallback"
        )

        data = {
            "name": "No Categories In DB",
            "featured_item": None,
            "items": [media.id],
            "terms": [],  # no user terms
            "text": "No categories in system"
        }

        post = PostCreationManager.create_post(data, user)
        
        # Now the manager should have used the fallback category
        assert post.pk is not None
        assert post.main_category == fallback_cat
        assert post.terms.count() == 0  # user provided no valid terms

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
