# posts/managers/post_creation_manager.py
import random
from django.db import transaction
from posts.models import Post, PostMedia
from taxonomy.models import Term
from media.models import MediaItem, MediaItemVersion
from media.jobs.dispatcher import TaskDispatcher
from main.providers.settings_provider import SettingsProvider
from main.utils import generate_unique_slug

class PostCreationManager:
    """
    Manager for creating a Post with associated media items.
    
    Workflow:
      1. Retrieve the post blur probability.
      2. Flip a coin to decide if the post is blurred.
      3. Create the Post with the determined `is_blurred` value.
      4. Create PostMedia links for associated MediaItems.
      5. For each MediaItem in the post:
            - If the post is blurred, enqueue creation of blurred versions.
            - Else, enqueue only standard versions.
    """
    
    @staticmethod
    def create_post(data, user):
        """
        Creates a Post with associated media items.
        
        Expected data keys:
          - name, text, featured_item, items (list of media item IDs), terms (list of term IDs)
        """
        # 1. Fetch the post blur probability.
        prob_str = SettingsProvider.get_setting("post_blur_probability")
        try:
            post_blur_probability = float(prob_str)
        except (TypeError, ValueError):
            post_blur_probability = 0.0  # Default to 0 if not set
        
        # 2. Flip a coin to determine if the post is blurred.
        is_blurred = random.random() < post_blur_probability

        with transaction.atomic():
            name = data.get("name")
            text = data.get("text", "")
            featured_item_id = data.get("featured_item")
            item_ids = data.get("items", [])
            term_ids = data.get("terms", [])
            
            # Validate and load media items belonging to the user.
            media_items = MediaItem.objects.filter(id__in=item_ids, owner=user)
            if media_items.count() != len(item_ids):
                raise ValueError("One or more media items do not exist or do not belong to you.")
            
            # Validate and load featured item if provided.
            featured_item_obj = None
            if featured_item_id is not None:
                try:
                    featured_item_obj = MediaItem.objects.get(id=featured_item_id, owner=user)
                except MediaItem.DoesNotExist:
                    raise ValueError("Featured item does not exist or does not belong to you.")
            
            # Validate and load terms.
            terms_qs = Term.objects.filter(id__in=term_ids)
            if term_ids and terms_qs.count() != len(term_ids):
                raise ValueError("One or more terms do not exist.")
            
            # Determine main_category.
            if term_ids:
                main_cat = terms_qs.filter(term_type=Term.CATEGORY).first()
                if not main_cat:
                    main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
            else:
                main_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
            if not main_cat:
                raise ValueError("No valid category found.")
            
            # Generate a unique slug for the post.
            slug = generate_unique_slug(Post, name, max_length=50)
            
            # 3. Create the Post with is_blurred property.
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
            
            # 4. Add terms to the post.
            if term_ids:
                post.terms.add(*terms_qs)
            
            # 5. Create PostMedia links for each media item.
            for pos, m_id in enumerate(item_ids):
                media_obj = media_items.get(id=m_id)
                PostMedia.objects.create(
                    post=post,
                    media_item=media_obj,
                    position=pos
                )
        
        # 6. Enqueue media version creation for each media item.
        # If the post is blurred, include blurred versions; otherwise, only standard versions.
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
            TaskDispatcher.dispatch_media_item_versions(
                media_item.id,
                regenerate=False,
                allowed_versions=allowed_versions
            )
        
        return post
