# tests/test_post_api.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from taxonomy.models import Term
from media.models import MediaItem

@pytest.mark.django_db
class TestPostAPI:
    def test_create_post_success(self, user_factory, media_item_factory, term_factory):
        """
        E2E test: create a post via API call, ensure response is correct and post is created.
        """
        user = user_factory()
        cat = term_factory(term_type=Term.CATEGORY)
        tag = term_factory(term_type=Term.TAG)
        media1 = media_item_factory(owner=user)
        media2 = media_item_factory(owner=user)

        payload = {
            "name": "E2E Test Post",
            "featured_item": media1.id,
            "items": [media1.id, media2.id],
            "terms": [cat.id, tag.id],
            "text": "Some content"
        }

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('create-post')  # or "/api/posts/new/" if direct path
        response = client.post(url, payload, format='json')

        assert response.status_code == 201, response.data
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "E2E Test Post"
        assert data["slug"]  # slug should be set
        # Check that terms were applied
        assert len(data["terms"]) == 2
        assert set(data["items"]) == {media1.id, media2.id}

    def test_create_post_partial_invalid_categories(self, user_factory, media_item_factory, term_factory):
        user = user_factory()
        media = media_item_factory(owner=user)
        # create a fallback category for the manager to pick up
        fallback_cat = term_factory(term_type=Term.CATEGORY, name="Default Category")

        payload = {
            "name": "Partial Invalid Categories",
            "featured_item": None,
            "items": [media.id],
            "terms": [999, 1000],  # presumably invalid
            "text": "Will still be created"
        }

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('create-post')
        response = client.post(url, payload, format='json')

        # By default, CreateAPIView returns 201 on success.
        assert response.status_code == 201, response.data
        
        data = response.json()
        # The manager should have used fallback_cat
        assert data["id"] is not None
        assert len(data["terms"]) == 0  # no valid user terms
        # if you want to confirm the fallback category is set:
        # retrieve the Post from DB and check its main_category
        from posts.models import Post
        post = Post.objects.get(pk=data["id"])
        assert post.main_category == fallback_cat
