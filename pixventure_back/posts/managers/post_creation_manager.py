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
         to process the required versions.
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
                    raise ValueError("Featured item does not exist or does not belong to you.")

            # Load only the valid terms
            valid_terms = Term.objects.filter(id__in=term_ids)

            # We skip invalid terms without crashing
            # (invalid IDs simply won't be in valid_terms)

            # 3. Attempt to find at least one category from the valid terms
            category_qs = valid_terms.filter(term_type=Term.CATEGORY)
            main_cat = get_mandatory_category(category_qs)  # This might raise if none is found

            # 4. Generate unique slug
            slug = generate_unique_slug(Post, name, max_length=50)

            # 5. Create the Post
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

            # 6. Attach all valid terms (including categories and tags)
            if valid_terms.exists():
                post.terms.add(*valid_terms)

            # 7. Create PostMedia links
            for pos, m_id in enumerate(item_ids):
                media_obj = media_items.get(id=m_id)
                PostMedia.objects.create(
                    post=post,
                    media_item=media_obj,
                    position=pos
                )

        # 8. Process media versions
        allowed_versions = [MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED]
        if is_blurred:
            allowed_versions += [MediaItemVersion.BLURRED_THUMBNAIL, MediaItemVersion.BLURRED_PREVIEW]

        for media_item in media_items:
            mvm = MediaVersionManager(media_item.id)
            mvm.process_versions(regenerate=False, allowed_versions=allowed_versions)

        return post
