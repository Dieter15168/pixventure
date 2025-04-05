import os
import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

# Attempt to use tqdm for a progress bar
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

from media.models import MediaItem, MediaItemVersion
from media.services import image_metadata, video_metadata
from media.services.hasher import compute_file_hash, compute_fuzzy_hash
from media.utils.video_loader import get_video_metadata  # or use video_metadata.extract_video_metadata
from media.services.video_metadata import extract_video_metadata
from media.services.image_metadata import extract_image_metadata
from media.models import HashType, MediaItemHash

class Command(BaseCommand):
    help = "Populates missing metadata (width, height, file_size) and hashes (blake3, phash) for MediaItemVersion. This command is useful for populating both metadata and hashes, fetching the file only once."

    def handle(self, *args, **options):
        self.stdout.write("→ Populating media version metadata and hashes...")

        # 1) Ensure HashTypes exist
        blake3_type, _ = HashType.objects.get_or_create(
            name='blake3',
            defaults={'description': 'BLAKE3 cryptographic hash'}
        )
        phash_type, _ = HashType.objects.get_or_create(
            name='phash',
            defaults={'description': 'Perceptual hash (phash) for images'}
        )

        # 2) Fetch all MediaItemVersion objects
        versions_qs = MediaItemVersion.objects.select_related('media_item').all()

        if TQDM_AVAILABLE:
            versions_iter = tqdm(versions_qs, desc="Processing Media Versions", unit="version")
        else:
            versions_iter = versions_qs

        updated_count = 0
        hash_count = 0

        with transaction.atomic():
            for version in versions_iter:
                file_field = version.file
                # If no file or empty path => skip
                if not file_field or not file_field.name:
                    continue

                media_item = version.media_item
                if not media_item:
                    continue

                # We only want to do a single file read for all operations
                # so we'll open it once as a file-like.
                try:
                    # "file_field.open()" => returns an open file-like
                    file_field.open('rb')
                except Exception:
                    # If file is missing (esp. in production with no local file), skip or handle as needed
                    continue

                try:
                    # 3) If metadata is missing, compute and update
                    #    We'll check if width/height/file_size is 0 or None
                    missing_metadata = (not version.width or not version.height or not version.file_size)
                    if missing_metadata:
                        if media_item.media_type == MediaItem.PHOTO:
                            # Attempt to treat as an image
                            meta = extract_image_metadata(file_field)
                            # meta => {"width":..., "height":..., "file_size":..., "format":...}
                            version.width = meta["width"]
                            version.height = meta["height"]
                            version.file_size = meta["file_size"]
                            version.save()
                            updated_count += 1
                        else:
                            # Attempt to treat as a video
                            # You could use either your "video_metadata.extract_video_metadata" or "get_video_metadata"
                            # For example:
                            meta = extract_video_metadata(file_field)
                            # meta => {"width":..., "height":..., "duration":...}
                            if meta["width"] and meta["height"]:
                                version.width = meta["width"]
                                version.height = meta["height"]
                            if "duration" in meta:
                                # If you want to store the duration, you'd need a field in MediaItemVersion
                                pass
                            # file_size is trickier for in-memory or remote storage
                            # if file_field.size is accessible, you can set it:
                            if hasattr(file_field, 'size'):
                                version.file_size = file_field.size
                            version.save()
                            updated_count += 1

                    # 4) Now compute or update the blake3 hash if missing
                    #    Check if there's already a MediaItemHash with hash_type=blake3
                    has_blake3 = version.hashes.filter(hash_type=blake3_type).exists()
                    if not has_blake3:
                        # re-seek file
                        file_field.seek(0)
                        b3_hex = compute_file_hash(file_field, hash_type="blake3")
                        file_field.seek(0)
                        # create the MediaItemHash row
                        MediaItemHash.objects.create(
                            media_item_version=version,
                            hash_type=blake3_type,
                            hash_value=b3_hex,
                        )
                        hash_count += 1

                    # 5) If version_type is ORIGINAL and media_type=PHOTO => compute phash if missing
                    #    version_type => version.ORIGINAL=0, THUMBNAIL=1, etc. See your choices.
                    #    We'll assume "ORIGINAL"=0 is the stored constant.
                    if (version.version_type == MediaItemVersion.ORIGINAL and
                        media_item.media_type == MediaItem.PHOTO):
                        has_phash = version.hashes.filter(hash_type=phash_type).exists()
                        if not has_phash:
                            file_field.seek(0)
                            fuzzy_hex = compute_fuzzy_hash(file_field, hash_type="phash")
                            file_field.seek(0)
                            MediaItemHash.objects.create(
                                media_item_version=version,
                                hash_type=phash_type,
                                hash_value=fuzzy_hex,
                            )
                            hash_count += 1

                finally:
                    # Always close the file
                    file_field.close()

        self.stdout.write(f"✓ Updated metadata for {updated_count} MediaItemVersions.")
        self.stdout.write(f"✓ Created/updated {hash_count} MediaItemHash records.")
        self.stdout.write("Done populating media metadata and hashes.")
