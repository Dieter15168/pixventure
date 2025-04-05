from django.db import connections, transaction

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from django.contrib.auth import get_user_model
from moderation.models import ModerationAction, RejectionReason
from media.models import MediaItem, MediaItemVersion

User = get_user_model()

# Old moderation statuses
MODERATION_STATUS_PENDING = 0
MODERATION_STATUS_APPROVED = 1

# Map old statuses > new
MEDIA_STATUS_PENDING = MediaItem.PENDING_MODERATION
MEDIA_STATUS_APPROVED = MediaItem.APPROVED
MEDIA_STATUS_REJECTED = MediaItem.REJECTED
MEDIA_STATUS_ARCHIVED = MediaItem.ARCHIVED

# Rejected statuses dictionary → new RejectionReason name
LEGACY_REJECTED_STATUSES = {
    2: "Low quality",
    3: "Underage",
    4: "Watermark, copyright mark or frame",
    5: "Not candid",
    6: "Sensitive content",
    7: "Duplicate of an existing item",
    8: "Duplicate of an existing item",
    9: "Needs re-rendering or file update",
    10: "Duplicate of an existing item (very similar)",
    11: "Wrong orientation, please rotate",
    12: "File is corrupted",
}

# We ensure these reasons are seeded
REJECTION_REASONS_SEED = [
    {
        "name": "Low quality",
        "description": "Low resolution, blurred, or otherwise low quality",
    },
    {
        "name": "Underage",
        "description": "Underage persons or underage nudity",
    },
    {
        "name": "Watermark, copyright mark or frame",
        "description": "Media contains third-party watermarks or frames",
    },
    {
        "name": "Not candid",
        "description": "Not candid",
    },
    {
        "name": "Sensitive content",
        "description": "Includes sensitive content",
    },
    {
        "name": "Duplicate of an existing item",
        "description": "Very similar to other uploaded items",
    },
    {
        "name": "Wrong orientation, please rotate",
        "description": "Image or video orientation is incorrect",
    },
    {
        "name": "File is corrupted",
        "description": "Cannot be opened or processed",
    },
    {
        "name": "Needs re-rendering or file update",
        "description": "Item was updated and needs to be re-rendered",
    },
]


def migrate_media_items():
    print("→ Migrating Post_item to MediaItem...")

    # 1) Ensure RejectionReasons exist
    reason_name_to_obj = {}
    for reason_data in REJECTION_REASONS_SEED:
        reason_obj, _ = RejectionReason.objects.using('default').update_or_create(
            name=reason_data["name"],
            defaults={
                "description": reason_data.get("description", ""),
                "is_active": True,
            }
        )
        reason_name_to_obj[reason_obj.name] = reason_obj

    # 2) Fetch legacy post items
    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                name,
                item_type,
                original_upload_date,
                publication_date,
                last_updated_date,
                belongs_to_user_id,
                height,
                width,
                file_format,
                file_size,
                original_filename,
                moderation_status,
                likes_counter,
                blurred_for_unregistered_users,
                blurred_for_non_paying_users,
                is_archived,
                original,
                watermarked_video,
                short_video_preview,
                watermarked_version,
                preview,
                thumbnail,
                blurred_preview,
                blurred_thumbnail
            FROM scgapp_post_item
        """)
        rows = cursor.fetchall()

    created_count = 0
    updated_count = 0
    versions_created_count = 0
    moderation_action_count = 0

    # Optional progress bar
    row_iter = rows
    if TQDM_AVAILABLE:
        row_iter = tqdm(rows, desc="Migrating Media Items", unit="item")

    with transaction.atomic(using='default'):
        for row in row_iter:
            (
                legacy_id,
                legacy_name,
                legacy_item_type,
                original_upload_date,
                publication_date,
                last_updated_date,
                belongs_to_user_id,
                height,
                width,
                file_format,
                file_size,
                original_filename,
                moderation_status,
                likes_counter,
                blurred_for_unreg,
                blurred_for_nonpay,
                is_archived,
                original_file,
                watermarked_video_file,
                short_video_preview_file,
                watermarked_version_file,
                preview_file,
                thumbnail_file,
                blurred_preview_file,
                blurred_thumbnail_file
            ) = row

            # Owner
            owner = None
            if belongs_to_user_id:
                try:
                    owner = User.objects.using('default').get(id=belongs_to_user_id)
                except User.DoesNotExist:
                    # If user doesn't exist, skip or do something else
                    continue

            # Determine media_type
            media_type = MediaItem.PHOTO if legacy_item_type == 1 else MediaItem.VIDEO

            # Step A: figure out if item was "rejected" in legacy
            if moderation_status == MODERATION_STATUS_PENDING:
                new_status = MEDIA_STATUS_PENDING
            elif moderation_status == MODERATION_STATUS_APPROVED:
                new_status = MEDIA_STATUS_APPROVED
            else:
                new_status = MEDIA_STATUS_REJECTED  # everything else is rejected

            # Step B: if is_archived is True, override final status to ARCHIVED
            # but note that if new_status was REJECTED, we STILL want to create a moderation action.
            is_rejected = (new_status == MEDIA_STATUS_REJECTED)
            if is_archived:
                new_status = MEDIA_STATUS_ARCHIVED

            # is_blurred => (blurred_for_unreg OR blurred_for_nonpay)
            is_blurred = bool(blurred_for_unreg or blurred_for_nonpay)

            # Create or update the MediaItem
            item, created_item = MediaItem.objects.using('default').update_or_create(
                original_filename=original_filename or f"legacy_{legacy_id}",
                owner=owner,
                defaults={
                    'media_type': media_type,
                    'status': new_status,
                    'likes_counter': likes_counter or 0,
                    'is_blurred': is_blurred,
                }
            )

            created_count += 1 if created_item else 0
            updated_count += 0 if created_item else 1

            # Overwrite created date with original_upload_date if present
            if original_upload_date:
                MediaItem.objects.using('default').filter(pk=item.pk).update(created=original_upload_date)
                item.refresh_from_db()

            # If legacy status was something in REJECTED, create a ModerationAction
            if is_rejected and moderation_status in LEGACY_REJECTED_STATUSES:
                reason_name = LEGACY_REJECTED_STATUSES[moderation_status]
                reason_obj = reason_name_to_obj.get(reason_name)

                # old_status typically = PENDING
                old_status = MEDIA_STATUS_PENDING

                action = ModerationAction.objects.using('default').create(
                    media_item=item,
                    old_status=old_status,
                    new_status=MEDIA_STATUS_REJECTED,
                    owner=owner,
                    moderator_id=1,  # your chosen staff user
                )
                if reason_obj:
                    action.rejection_reasons.add(reason_obj)
                moderation_action_count += 1

            # Create or update MediaItemVersion for each file path
            def create_version(file_path, version_type, w=None, h=None, size=None):
                nonlocal versions_created_count
                if file_path:
                    _, created_ver = MediaItemVersion.objects.using('default').update_or_create(
                        media_item=item,
                        version_type=version_type,
                        defaults={
                            'file': file_path,
                            'width': w,
                            'height': h,
                            'file_size': size,
                        }
                    )
                    if created_ver:
                        versions_created_count += 1

            # original gets height/width/size
            create_version(original_file, MediaItemVersion.ORIGINAL, w=width, h=height, size=file_size)
            create_version(watermarked_video_file, MediaItemVersion.WATERMARKED)
            create_version(watermarked_version_file, MediaItemVersion.WATERMARKED)
            create_version(short_video_preview_file, MediaItemVersion.PREVIEW)
            create_version(preview_file, MediaItemVersion.PREVIEW)
            create_version(thumbnail_file, MediaItemVersion.THUMBNAIL)
            create_version(blurred_preview_file, MediaItemVersion.BLURRED_PREVIEW)
            create_version(blurred_thumbnail_file, MediaItemVersion.BLURRED_THUMBNAIL)

    print(f"✓ Created: {created_count} / Updated: {updated_count} MediaItem records.")
    print(f"✓ Created {versions_created_count} MediaItemVersion records.")
    print(f"✓ Created {moderation_action_count} ModerationAction records.")
