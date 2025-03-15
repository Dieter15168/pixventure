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
            Determine which versions to create based on media item and related post attributes.
            Previews and full watermarked versions are always generated.
            Blurred versions are generated if media_item.is_blurred is True
            or if media_item.post.is_blurred is True.
            """
            allowed = [MediaItemVersion.PREVIEW, MediaItemVersion.WATERMARKED]
            # Check media item flag and, if available, its related post flag.
            if media_item.is_blurred or (hasattr(media_item, 'post') and media_item.post.is_blurred):
                allowed.extend([MediaItemVersion.BLURRED_THUMBNAIL, MediaItemVersion.BLURRED_PREVIEW])
            return allowed

        if media_item_id:
            try:
                media_item = MediaItem.objects.get(id=media_item_id)
                allowed_versions = determine_allowed_versions(media_item)
                TaskDispatcher.dispatch_media_item_versions(media_item_id, regenerate=regenerate, allowed_versions=allowed_versions)
                self.stdout.write(self.style.SUCCESS(f"Queued processing for MediaItem {media_item_id} with versions: {allowed_versions}"))
            except MediaItem.DoesNotExist:
                raise CommandError(f"MediaItem with ID {media_item_id} does not exist.")
        else:
            qs = MediaItem.objects.filter(status=MediaItem.PENDING_MODERATION)
            for item in qs:
                allowed_versions = determine_allowed_versions(item)
                TaskDispatcher.dispatch_media_item_versions(item.id, regenerate=regenerate, allowed_versions=allowed_versions)
            self.stdout.write(self.style.SUCCESS("Queued processing for all pending MediaItems."))
