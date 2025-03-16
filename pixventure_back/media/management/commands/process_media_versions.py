# media/management/commands/process_media_versions.py
from django.core.management.base import BaseCommand, CommandError
from media.models import MediaItem, MediaItemVersion
from media.jobs.dispatcher import TaskDispatcher

class Command(BaseCommand):
    help = "Enqueue asynchronous tasks to process additional media item versions based on specified criteria."

    def add_arguments(self, parser):
        parser.add_argument(
            'media_item_id',
            type=int,
            nargs='?',
            help='Optional: ID of the MediaItem to process. If omitted, processes all pending items.'
        )
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Force regeneration of versions even if they already exist.'
        )

    def handle(self, *args, **options):
        regenerate = options.get('regenerate', False)
        media_item_id = options.get('media_item_id')

        def determine_allowed_versions(media_item):
            """
            Determine which versions should be created.
            For images:
            - Always require PREVIEW and WATERMARKED.
            - If the item (or its related post) is blurred, also require BLURRED_THUMBNAIL and BLURRED_PREVIEW.
            For videos:
            - Always require WATERMARKED, PREVIEW, and THUMBNAIL.
            """
            from media.models import MediaItem  # Assuming MediaItem.PHOTO and MediaItem.VIDEO exist

            if media_item.media_type == MediaItem.VIDEO:
                # For videos, always include THUMBNAIL
                return [MediaItemVersion.WATERMARKED, MediaItemVersion.PREVIEW, MediaItemVersion.THUMBNAIL]
            else:
                allowed = [MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED]
                if media_item.is_blurred or (hasattr(media_item, 'post') and media_item.post.is_blurred):
                    allowed.extend([MediaItemVersion.BLURRED_THUMBNAIL, MediaItemVersion.BLURRED_PREVIEW])
                return allowed


        def missing_versions(media_item, allowed_versions):
            """
            Given a media item and the allowed_versions list, return a list of versions that are missing.
            """
            existing = set(media_item.versions.values_list('version_type', flat=True))
            return [v for v in allowed_versions if v not in existing]

        if media_item_id:
            try:
                media_item = MediaItem.objects.get(id=media_item_id)
                allowed_versions = determine_allowed_versions(media_item)
                if not regenerate:
                    allowed_versions = missing_versions(media_item, allowed_versions)
                if not allowed_versions:
                    self.stdout.write(self.style.WARNING(
                        f"MediaItem {media_item_id} already has all required versions."
                    ))
                else:
                    TaskDispatcher.dispatch_media_item_versions(
                        media_item_id,
                        regenerate=regenerate,
                        allowed_versions=allowed_versions
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"Queued processing for MediaItem {media_item_id} with versions: {allowed_versions}"
                    ))
            except MediaItem.DoesNotExist:
                raise CommandError(f"MediaItem with ID {media_item_id} does not exist.")
        else:
            qs = MediaItem.objects.filter(status=MediaItem.PENDING_MODERATION)
            processed, skipped = 0, 0
            for item in qs:
                allowed_versions = determine_allowed_versions(item)
                if not regenerate:
                    allowed_versions = missing_versions(item, allowed_versions)
                if allowed_versions:
                    TaskDispatcher.dispatch_media_item_versions(item.id, regenerate=regenerate, allowed_versions=allowed_versions)
                    processed += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Queued processing for MediaItem {item.id} with versions: {allowed_versions}"
                    ))
                else:
                    skipped += 1
                    self.stdout.write(self.style.WARNING(
                        f"MediaItem {item.id} already has all required versions; skipping."
                    ))
            self.stdout.write(self.style.SUCCESS(
                f"Queued processing for {processed} items; {skipped} items were skipped."
            ))
