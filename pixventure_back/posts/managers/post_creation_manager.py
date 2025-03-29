# posts/managers/post_creation_manager.py

import random
from django.db import transaction
from posts.models import Post, PostMedia
from taxonomy.models import Term
from media.models import MediaItem, MediaItemVersion
from main.providers.settings_provider import SettingsProvider
from main.utils import generate_unique_slug
from media.managers.media_versions.media_version_manager import MediaVersionManager
from taxonomy.utils import get_mandatory_category

class PostCreationManager:
    """
    Manager for creating a Post with associated media items.

    Workflow:
      1. Retrieve the post blur probability.
      2. Flip a coin to decide if the post is blurred.
      3. Create the Post with the determined `is_blurred` value.
      4. Attach valid terms and set main_category if possible.
      5. Create PostMedia links for associated MediaItems.
      6. For each media item in the post, call MediaVersionManager
         to process only the required versions that do not already exist.
    """

    @staticmethod
    def create_post(data, user):
        # 1. Fetch post blur probability
        prob_str = SettingsProvider.get_setting("post_blur_probability")
        try:
            post_blur_probability = float(prob_str)
        except (TypeError, ValueError):
            post_blur_probability = 0.0  # Default to 0 if invalid

        # 2. Decide if the post should be blurred
        is_blurred = random.random() < post_blur_probability

        with transaction.atomic():
            name = data.get('name')
            text = data.get('text', "")
            featured_item_id = data.get('featured_item')
            item_ids = data.get('items', [])
            term_ids = data.get('terms', [])  # might contain invalid IDs

            # Validate media items (these must be valid; otherwise, we fail).
            media_items = MediaItem.objects.filter(id__in=item_ids, owner=user)
            if media_items.count() != len(item_ids):
                raise ValueError("One or more media items do not exist or do not belong to you.")

            # Validate featured item
            featured_item_obj = None
            if featured_item_id is not None:
                try:
                    featured_item_obj = MediaItem.objects.get(id=featured_item_id, owner=user)
                except MediaItem.DoesNotExist:
                    raise ValueError("Featured item does not exist or do not belong to you.")

            # Load only the valid terms
            valid_terms = Term.objects.filter(id__in=term_ids)

            # Attempt to find at least one category from the valid terms
            category_qs = valid_terms.filter(term_type=Term.CATEGORY)
            main_cat = get_mandatory_category(category_qs)  # Might raise if none found

            # 3. Generate unique slug
            slug = generate_unique_slug(Post, name, max_length=50)

            # 4. Create the Post
            post = Post.objects.create(
                owner=user,
                name=name,
                slug=slug,
                text=text,
                featured_item=featured_item_obj,
                main_category=main_cat,
                status=Post.PENDING_MODERATION,
                is_blurred=is_blurred
            )

            # 5. Attach all valid terms
            if valid_terms.exists():
                post.terms.add(*valid_terms)

            # 6. Create PostMedia links
            for pos, m_id in enumerate(item_ids):
                media_obj = media_items.get(id=m_id)
                PostMedia.objects.create(
                    post=post,
                    media_item=media_obj,
                    position=pos
                )

        # 7. Process media versions (only if they do not already exist)
        #    If post is blurred, we also need blurred variants.
        allowed_versions = [MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED]
        if is_blurred:
            # Adjust these as needed if your model names differ 
            allowed_versions += [
                MediaItemVersion.BLURRED_PREVIEW,
                MediaItemVersion.BLURRED_THUMBNAIL
            ]
        print(allowed_versions)

        for media_item in media_items:
            existing_version_types = MediaItemVersion.objects.filter(
                media_item=media_item,
                version_type__in=allowed_versions
            ).values_list('version_type', flat=True)
            print(existing_version_types)

            # Filter down to only the versions that do not yet exist.
            versions_to_create = [v for v in allowed_versions if v not in existing_version_types]
            print(versions_to_create)

            # If we have anything left to create, do so.
            if versions_to_create:
                mvm = MediaVersionManager(media_item.id)
                mvm.process_versions(regenerate=False, allowed_versions=versions_to_create)

        return post
