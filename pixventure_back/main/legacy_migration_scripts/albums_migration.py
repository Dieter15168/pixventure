import json
from django.db import connections, transaction
from django.utils import timezone

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from django.contrib.auth import get_user_model
from albums.models import Album, AlbumElement
from media.models import MediaItem
from posts.models import Post

User = get_user_model()

def migrate_albums():
    print("→ Migrating legacy Album -> new Album / AlbumElement ...")

    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT 
                a.id,
                a.name,
                a.slug,
                a.belongs_to_user_id,
                a.creation_date,
                a.is_public,
                a.show_album_creator_to_other_users,
                a.likes_counter,
                a.is_archived,
                a.order_of_items
            FROM scgapp_album a
            ORDER BY a.id
        """)
        rows = cursor.fetchall()

    row_iter = rows
    if TQDM_AVAILABLE:
        row_iter = tqdm(rows, desc="Migrating Albums")

    created_count = 0
    updated_count = 0
    element_count = 0
    skipped_empty_albums = 0

    with transaction.atomic(using='default'):
        for row in row_iter:
            (
                legacy_id,
                name,
                slug,
                belongs_to_user_id,
                creation_date,
                is_public,
                show_creator,
                likes_counter,
                is_archived,
                order_of_items_json,
            ) = row

            # Parse order_of_items
            try:
                order_list = json.loads(order_of_items_json or "[]")
                if not isinstance(order_list, list):
                    order_list = []
            except Exception:
                order_list = []

            # Skip if album is empty
            if not order_list:
                skipped_empty_albums += 1
                continue

            # Determine album owner
            owner = None
            if belongs_to_user_id:
                try:
                    owner = User.objects.using('default').get(id=belongs_to_user_id)
                except User.DoesNotExist:
                    pass

            # Convert old booleans to new album status
            # If is_archived => ARCHIVED, else if is_public => PUBLISHED, else PRIVATE
            if is_archived:
                new_status = Album.ARCHIVED
            else:
                new_status = Album.PUBLISHED if is_public else Album.PRIVATE

            # Upsert the new Album
            album_obj, created = Album.objects.using('default').update_or_create(
                slug=slug,
                name=name,
                owner=owner,
                defaults={
                    'status': new_status,
                    'likes_counter': likes_counter or 0,
                    'show_creator_to_others': show_creator,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            # Overwrite created date
            if creation_date:
                Album.objects.using('default').filter(pk=album_obj.pk).update(created=creation_date)
                album_obj.refresh_from_db()

            # Build AlbumElements from order_list
            position = 0
            for element_data in order_list:
                # Expect [id, object_type]
                if not (isinstance(element_data, list) and len(element_data) == 2):
                    continue

                legacy_object_id, legacy_object_type = element_data

                if legacy_object_type == 1:
                    # It's a Post
                    with connections['legacy'].cursor() as post_cur:
                        post_cur.execute("SELECT slug FROM scgapp_post WHERE id=%s", [legacy_object_id])
                        p_res = post_cur.fetchone()
                    if p_res:
                        old_slug = p_res[0]
                        new_post = Post.objects.using('default').filter(slug=old_slug).first()
                        if new_post:
                            AlbumElement.objects.using('default').create(
                                album=album_obj,
                                element_type=AlbumElement.POST_TYPE,
                                element_post=new_post,
                                position=position
                            )
                            element_count += 1
                            position += 1

                elif legacy_object_type == 2:
                    # It's a Post_item => new MediaItem
                    with connections['legacy'].cursor() as item_cur:
                        item_cur.execute("SELECT original_filename FROM scgapp_post_item WHERE id=%s", [legacy_object_id])
                        i_res = item_cur.fetchone()
                    if i_res:
                        old_fname = i_res[0] or f"legacy_{legacy_object_id}"
                        new_media = MediaItem.objects.using('default').filter(original_filename=old_fname).first()
                        if new_media:
                            AlbumElement.objects.using('default').create(
                                album=album_obj,
                                element_type=AlbumElement.MEDIA_TYPE,
                                element_media=new_media,
                                position=position
                            )
                            element_count += 1
                            position += 1

            # After building all album elements, update featured_item
            album_obj.update_featured_item()

    print(f"\n--- Albums Migration Summary ---")
    print(f"Skipped empty albums: {skipped_empty_albums}")
    print(f"Created {created_count}, Updated {updated_count} Albums.")
    print(f"Created {element_count} AlbumElements.")
    print("Album migration complete.")
