import json
from django.db import connections, transaction
from django.utils import timezone

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from django.contrib.auth import get_user_model
from moderation.models import ModerationAction, RejectionReason
from media.models import MediaItem
from posts.models import Post, PostMedia
from taxonomy.models import Term

User = get_user_model()

# Legacy statuses
NOT_PROCESSED = 0
APPROVED = 1
ALL_ITEMS_REJECTED = 2
FOUL_LANGUAGE_IN_TEXT = 3
INCORRECT_CATEGORIES = 4
INCORRECT_TAGS = 5
NO_TAGS = 6
SENSITIVE_CONTENT_OR_PRIVATE_INFO = 7

# New Post statuses
PENDING_MODERATION = Post.PENDING_MODERATION
APPROVED_NEW      = Post.APPROVED
REJECTED_NEW      = Post.REJECTED
ARCHIVED_NEW      = Post.ARCHIVED
PUBLISHED_NEW     = Post.PUBLISHED

# RejectionReason mapping for rejected posts
LEGACY_POST_REJECTED_MAP = {
    ALL_ITEMS_REJECTED: "All items were rejected",
    FOUL_LANGUAGE_IN_TEXT: "Foul language",
    INCORRECT_CATEGORIES: "Incorrect categories",
    INCORRECT_TAGS: "Incorrect tags",
    NO_TAGS: "No tags",
    SENSITIVE_CONTENT_OR_PRIVATE_INFO: "Sensitive or private information",
}

REJECTION_REASONS_POST = [
    {
        "name": "All items were rejected",
        "description": "All photos or videos in this post were rejected by moderation",
    },
    {
        "name": "Foul language",
        "description": "Contains offensive or foul language",
    },
    {
        "name": "Incorrect categories",
        "description": "Categories assigned do not match post content",
    },
    {
        "name": "Incorrect tags",
        "description": "Tags assigned do not match post content",
    },
    {
        "name": "No tags",
        "description": "Post requires tags, none were provided",
    },
    {
        "name": "Sensitive or private information",
        "description": "Potentially revealing private details or sensitive information",
    },
]


def migrate_posts():
    print("→ Migrating legacy Post -> new Post/PostMedia...")

    # 1) Ensure RejectionReasons exist
    reason_name_to_obj = {}
    for reason_data in REJECTION_REASONS_POST:
        obj, _ = RejectionReason.objects.using('default').update_or_create(
            name=reason_data["name"],
            defaults={
                "description": reason_data.get("description", ""),
                "is_active": True,
            }
        )
        reason_name_to_obj[obj.name] = obj

    # 2) Find the smallest-ID Category in the new DB for fallback
    default_category = Term.objects.using('default') \
        .filter(term_type=Term.CATEGORY) \
        .order_by('id') \
        .first()
    if not default_category:
        raise ValueError("No Category found in the new DB to use as default.")

    # 3) Load legacy posts using LEFT JOIN to gather terms & included post items
    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT
                p.id,
                p.name,
                p.slug,
                p.text,
                p.creation_date,
                p.publication_date,
                p.last_updated_date,
                p.belongs_to_user_id,
                p.moderation_status,
                p.featured_item_id,
                p.likes_counter,
                p.blurred_for_unregistered_users,
                p.blurred_for_non_paying_users,
                p.is_approved_for_main_page_feeds,
                p.main_category_id,
                p.is_published,
                p.is_archived,

                array_agg(DISTINCT t.id) FILTER (WHERE t.id IS NOT NULL) AS legacy_term_ids,
                array_agg(DISTINCT pi.id) FILTER (WHERE pi.id IS NOT NULL) AS included_item_ids

            FROM scgapp_post p
            LEFT JOIN scgapp_post_is_marked_with_term link_t ON link_t.post_id = p.id
            LEFT JOIN scgapp_term t ON link_t.term_id = t.id

            LEFT JOIN scgapp_post_items_included link_i ON link_i.post_id = p.id
            LEFT JOIN scgapp_post_item pi ON link_i.post_item_id = pi.id

            GROUP BY p.id
            ORDER BY p.id
        """)
        rows = cursor.fetchall()

    # Optional progress bar
    row_iter = rows
    if TQDM_AVAILABLE:
        row_iter = tqdm(rows, desc="Migrating Posts")

    created_posts = 0
    updated_posts = 0
    moderation_actions_created = 0
    post_media_links_created = 0

    with transaction.atomic(using='default'):
        for row in row_iter:
            (
                legacy_id,
                name,
                slug,
                text,
                creation_date,
                publication_date,
                last_updated_date,
                belongs_to_user_id,
                legacy_mod_status,
                featured_item_id,
                likes_counter,
                blurred_for_unreg,
                blurred_for_nonpay,
                is_featured,
                main_category_id,
                is_published,
                is_archived,
                term_ids_array,
                included_item_ids,
            ) = row

            # Determine owner
            owner = None
            if belongs_to_user_id:
                try:
                    owner = User.objects.using('default').get(id=belongs_to_user_id)
                except User.DoesNotExist:
                    pass

            # Convert old moderation_status to new
            new_status = PENDING_MODERATION
            if legacy_mod_status == NOT_PROCESSED:
                new_status = PENDING_MODERATION
            elif legacy_mod_status == APPROVED:
                new_status = APPROVED_NEW
            else:
                new_status = REJECTED_NEW
            was_rejected = (new_status == REJECTED_NEW)

            # Archived overrides all, but we still create a moderation action if was_rejected
            if is_archived:
                new_status = ARCHIVED_NEW
            else:
                # If not archived, check if published
                if is_published:
                    new_status = PUBLISHED_NEW

            is_blurred = bool(blurred_for_unreg or blurred_for_nonpay)

            # Upsert Post with fallback main_category from the start
            post_obj, created = Post.objects.using('default').update_or_create(
                slug=slug,
                name=name,
                owner=owner,
                defaults={
                    'text': text,
                    'status': new_status,
                    'likes_counter': likes_counter or 0,
                    'is_blurred': is_blurred,
                    'is_featured_post': is_featured,
                    'main_category': default_category,
                }
            )

            if created:
                created_posts += 1
            else:
                updated_posts += 1

            # Overwrite created date if available
            if creation_date:
                Post.objects.using('default').filter(pk=post_obj.pk).update(created=creation_date)
                post_obj.refresh_from_db()

            # If final status= PUBLISHED => published=publication_date
            if post_obj.status == PUBLISHED_NEW and publication_date:
                Post.objects.using('default').filter(pk=post_obj.pk).update(published=publication_date)
                post_obj.refresh_from_db()

            # Create ModerationAction if rejected
            if was_rejected and legacy_mod_status in LEGACY_POST_REJECTED_MAP:
                reason_name = LEGACY_POST_REJECTED_MAP[legacy_mod_status]
                reason_obj = reason_name_to_obj.get(reason_name)
                old_status = PENDING_MODERATION

                action = ModerationAction.objects.using('default').create(
                    post=post_obj,
                    old_status=old_status,
                    new_status=new_status,
                    owner=owner,
                    moderator_id=1,  # or another staff user
                )
                if reason_obj:
                    action.rejection_reasons.add(reason_obj)
                moderation_actions_created += 1

            # If the legacy DB indicates a main_category, try to map it now
            if main_category_id:
                with connections['legacy'].cursor() as cat_cur:
                    cat_cur.execute("SELECT name, slug, type FROM scgapp_term WHERE id=%s", [main_category_id])
                    cat_row = cat_cur.fetchone()
                if cat_row:
                    cat_name, cat_slug, cat_type = cat_row
                    # old type: 1 => category, 2 => tag
                    new_type = Term.CATEGORY if cat_type == 1 else Term.TAG
                    main_cat_obj = Term.objects.using('default').filter(term_type=new_type, slug=cat_slug).first()
                    if main_cat_obj:
                        post_obj.main_category = main_cat_obj
                        post_obj.save()

            # Terms M2M from term_ids_array
            if term_ids_array:
                for old_term_id in term_ids_array:
                    if not old_term_id:
                        continue
                    with connections['legacy'].cursor() as t_cur:
                        t_cur.execute("SELECT slug, type FROM scgapp_term WHERE id=%s", [old_term_id])
                        res = t_cur.fetchone()
                    if res:
                        slug_, type_ = res
                        new_type = Term.CATEGORY if type_ == 1 else Term.TAG
                        new_term = Term.objects.using('default').filter(term_type=new_type, slug=slug_).first()
                        if new_term:
                            post_obj.terms.add(new_term)

            # featured_item
            if featured_item_id:
                with connections['legacy'].cursor() as fi_cur:
                    fi_cur.execute("SELECT original_filename FROM scgapp_post_item WHERE id=%s", [featured_item_id])
                    fi_res = fi_cur.fetchone()
                if fi_res:
                    old_featured_filename = fi_res[0] or f"legacy_{featured_item_id}"
                    media_item = MediaItem.objects.using('default').filter(
                        original_filename=old_featured_filename
                    ).first()
                    if media_item:
                        post_obj.featured_item = media_item
                        post_obj.save()

            # 4) Link included items in natural index order
            if included_item_ids:
                for idx, old_item_id in enumerate(included_item_ids):
                    if not old_item_id:
                        continue
                    with connections['legacy'].cursor() as micur:
                        micur.execute("SELECT original_filename FROM scgapp_post_item WHERE id=%s", [old_item_id])
                        r = micur.fetchone()
                    if r:
                        old_fname = r[0] or f"legacy_{old_item_id}"
                        media = MediaItem.objects.using('default').filter(original_filename=old_fname).first()
                        if media:
                            pm, pm_created = PostMedia.objects.using('default').update_or_create(
                                post=post_obj,
                                media_item=media,
                                defaults={'position': idx},
                            )
                            if pm_created:
                                post_media_links_created += 1

            # 5) If final post status is PUBLISHED => set all APPROVED media to PUBLISHED
            if post_obj.status == PUBLISHED_NEW:
                mlinks = post_obj.post_media_links.all()
                for link in mlinks:
                    if link.media_item.status == MediaItem.APPROVED:
                        link.media_item.status = MediaItem.PUBLISHED
                        link.media_item.save(using='default')

    print(f"✓ Created {created_posts}, Updated {updated_posts} posts.")
    print(f"✓ Created {moderation_actions_created} moderation actions.")
    print(f"✓ Created/linked {post_media_links_created} PostMedia items.")
    print("Post migration complete.")
