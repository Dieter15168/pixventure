# media/management/commands/process_media_versions.py
from django.core.management.base import BaseCommand, CommandError
from media.models import MediaItem
from media.tasks import process_media_item_versions

class Command(BaseCommand):
    help = "Enqueue asynchronous tasks to process additional media item versions."

    def add_arguments(self, parser):
        parser.add_argument(
            'media_item_id', 
            type=int, 
            nargs='?', 
            help='Optional: ID of the MediaItem to process. If omitted, processes all pending items.'
        )

    def handle(self, *args, **options):
        media_item_id = options.get('media_item_id')
        if media_item_id:
            try:
                MediaItem.objects.get(id=media_item_id)
                process_media_item_versions.delay(media_item_id)
                self.stdout.write(self.style.SUCCESS(f"Queued processing for MediaItem {media_item_id}."))
            except MediaItem.DoesNotExist:
                raise CommandError(f"MediaItem with ID {media_item_id} does not exist.")
        else:
            qs = MediaItem.objects.filter(status=MediaItem.PENDING_MODERATION)
            for item in qs:
                process_media_item_versions.delay(item.id)
            self.stdout.write(self.style.SUCCESS("Queued processing for all pending MediaItems."))
