import json
from django.db import connections, transaction
from django.utils import timezone

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from django.contrib.auth import get_user_model
from social.models import Like as NewLike
from posts.models import Post
from media.models import MediaItem
from albums.models import Album

User = get_user_model()

def migrate_likes():
    print("→ Migrating legacy Like -> new social.Like ...")

    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                creation_date,
                liked_by_this_registered_user_id,
                belongs_to_user_id,
                belongs_to_item_id,
                belongs_to_post_id,
                belongs_to_album_id
            FROM scgapp_like
            ORDER BY id
        """)
        rows = cursor.fetchall()

    row_iter = rows
    if TQDM_AVAILABLE:
        row_iter = tqdm(rows, desc="Migrating Likes")

    created_likes = 0

    with transaction.atomic(using='default'):
        for row in row_iter:
            (
                legacy_like_id,
                creation_date,
                liked_by_this_registered_user_id,
                belongs_to_user_id,
                belongs_to_item_id,
                belongs_to_post_id,
                belongs_to_album_id
            ) = row

            # 1) Determine the "liking_user" from old "liked_by_this_registered_user"
            liking_user = None
            if liked_by_this_registered_user_id:
                try:
                    liking_user = User.objects.using('default').get(id=liked_by_this_registered_user_id)
                except User.DoesNotExist:
                    # user not found, skip or proceed with None
                    pass

            # 2) Collect references for each target type that is not null
            #    Because the new model can only reference one target per row,
            #    if multiple are set, we create multiple Like objects.
            targets = []

            # belongs_to_user => liked_user
            if belongs_to_user_id:
                # In old DB, belongs_to_user references user_meta => new "liked_user" is an actual user
                # But 'User_meta' in new system is linked 1:1 with user. So we can match
                # the old user_meta => user ID if you migrated them directly by ID. 
                # Or if you have a "is_extension_of_user" approach, you can do a sub-query 
                # to find the user. 
                
                # For simplicity, let's assume the user_meta had the same ID as the user, or you tracked it.
                # If that's not the case, you need a subquery to user_meta -> user => user.id
                # Example:
                # SELECT is_extension_of_user_id from scgapp_user_meta where id=belongs_to_user_id
                # Then that result is the actual user id in the new system.

                with connections['legacy'].cursor() as meta_cur:
                    meta_cur.execute("SELECT is_extension_of_user_id FROM scgapp_user_meta WHERE id=%s", [belongs_to_user_id])
                    meta_res = meta_cur.fetchone()
                if meta_res:
                    real_user_id = meta_res[0]
                    try:
                        liked_user = User.objects.using('default').get(id=real_user_id)
                        targets.append(('liked_user', liked_user))
                    except User.DoesNotExist:
                        pass

            # belongs_to_item => media_item
            if belongs_to_item_id:
                # old scgapp_post_item => new media
                with connections['legacy'].cursor() as item_cur:
                    item_cur.execute("SELECT original_filename FROM scgapp_post_item WHERE id=%s", [belongs_to_item_id])
                    i_res = item_cur.fetchone()
                if i_res:
                    old_fname = i_res[0] or f"legacy_{belongs_to_item_id}"
                    new_media = MediaItem.objects.using('default').filter(original_filename=old_fname).first()
                    if new_media:
                        targets.append(('media_item', new_media))

            # belongs_to_post => post
            if belongs_to_post_id:
                # old scgapp_post => new post
                with connections['legacy'].cursor() as post_cur:
                    post_cur.execute("SELECT slug FROM scgapp_post WHERE id=%s", [belongs_to_post_id])
                    p_res = post_cur.fetchone()
                if p_res:
                    old_slug = p_res[0]
                    new_post = Post.objects.using('default').filter(slug=old_slug).first()
                    if new_post:
                        targets.append(('post', new_post))

            # belongs_to_album => album
            if belongs_to_album_id:
                # old scgapp_album => new album 
                # matching by slug? 
                with connections['legacy'].cursor() as alb_cur:
                    alb_cur.execute("SELECT slug FROM scgapp_album WHERE id=%s", [belongs_to_album_id])
                    a_res = alb_cur.fetchone()
                if a_res:
                    old_album_slug = a_res[0]
                    new_album = Album.objects.using('default').filter(slug=old_album_slug).first()
                    if new_album:
                        targets.append(('album', new_album))

            # 3) For each target found, create a new Like
            for field_name, target_obj in targets:
                # Create the new Like
                like_obj = NewLike.objects.using('default').create(
                    liking_user=liking_user,
                    is_active=True,
                    # We'll fill the specific field with 'target_obj' below,
                    # but we can't do dynamic field assignment in create(...).
                    # Instead, we'll do an update after creation 
                    # or do a small approach like a dictionary approach. 
                    # Easiest is: handle each target field in separate if statements 
                    # or do a small "kwargs" approach:
                )

                # Now set the correct field
                if field_name == 'liked_user':
                    like_obj.liked_user = target_obj
                elif field_name == 'media_item':
                    like_obj.media_item = target_obj
                elif field_name == 'post':
                    like_obj.post = target_obj
                elif field_name == 'album':
                    like_obj.album = target_obj

                like_obj.save(using='default')

                # Overwrite created date with legacy creation_date
                if creation_date:
                    NewLike.objects.using('default').filter(pk=like_obj.pk).update(created=creation_date)
                    like_obj.refresh_from_db()

                created_likes += 1

    print(f"\n--- Likes Migration Summary ---")
    print(f"Created {created_likes} new Like objects.")
    print("Likes migration complete.")
