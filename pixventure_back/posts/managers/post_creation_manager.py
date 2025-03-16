# posts/managers/post_creation_manager.py
import random
from django.db import transaction
from posts.models import Post, PostMedia
from taxonomy.models import Term
from media.models import MediaItem, MediaItemVersion
from main.providers.settings_provider import SettingsProvider
from main.utils import generate_unique_slug
from media.managers.media_versions.media_version_manager import MediaVersionManager

class PostCreationManager:
    """
    Manager for creating a Post with associated media items.
    
    Workflow:
      1. Retrieve the post blur probability.
      2. Flip a coin to decide if the post is blurred.
      3. Create the Post with the determined `is_blurred` value.
      4. Create PostMedia links for associated MediaItems.
      5. For each media item in the post, call the MediaVersionManager
         to process the required versions.
    """
    
    @staticmethod
    def create_post(data, user):
        # 1. Fetch post blur probability.
        prob_str = SettingsProvider.get_setting("post_blur_probability")
        try:
            post_blur_probability = float(prob_str)
        except (TypeError, ValueError):
            post_blur_probability = 0.0  # Default
        
        # 2. Decide if the post should be blurred.
        is_blurred = random.random() < post_blur_probability

        with transaction.atomic():
            name = data.get('name')
            text = data.get('text', "")
            featured_item_id = data.get('featured_item')
            item_ids = data.get('items', [])
            term_ids = data.get('terms', [])
            
            # Validate media items.
            media_items = MediaItem.objects.filter(id__in=item_ids, owner=user)
            if media_items.count() != len(item_ids):
                raise ValueError("One or more media items do not exist or do not belong to you.")
            
            # Validate featured item.
            featured_item_obj = None
            if featured_item_id is not None:
                try:
                    featured_item_obj = MediaItem.objects.get(id=featured_item_id, owner=user)
                except MediaItem.DoesNotExist:
                    raise ValueError("Featured item does not exist or does not belong to you.")
            
            # Validate terms.
            terms_qs = Term.objects.filter(id__in=term_ids)
            if term_ids and terms_qs.count() != len(term_ids):
                raise ValueError("One or more terms do not exist.")
            
            # Determine main category.
            if term_ids:
                main_cat = terms_qs.filter(term_type=Term.CATEGORY).first()
                if not main_cat:
                    main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
            else:
                main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
            if not main_cat:
                raise ValueError("No valid category found.")
            
            # Generate unique slug.
            slug = generate_unique_slug(Post, name, max_length=50)
            
            # 3. Create the Post.
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
            
            # 4. Create PostMedia links.
            for pos, m_id in enumerate(item_ids):
                media_obj = media_items.get(id=m_id)
                PostMedia.objects.create(
                    post=post,
                    media_item=media_obj,
                    position=pos
                )
        
        # 5. For each media item, delegate version creation to MediaVersionManager.
        for media_item in media_items:
            if is_blurred:
                allowed_versions = [
                    MediaItemVersion.PREVIEW,
                    MediaItemVersion.WATERMARKED,
                    MediaItemVersion.BLURRED_THUMBNAIL,
                    MediaItemVersion.BLURRED_PREVIEW,
                ]
            else:
                allowed_versions = [
                    MediaItemVersion.PREVIEW,
                    MediaItemVersion.WATERMARKED,
                ]
            mvm = MediaVersionManager(media_item.id)
            mvm.process_versions(regenerate=False, allowed_versions=allowed_versions)
        
        return post
