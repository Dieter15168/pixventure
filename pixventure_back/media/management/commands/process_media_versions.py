# media/management/commands/process_media_versions.py
from django.core.management.base import BaseCommand, CommandError
from media.models import MediaItem, MediaItemVersion
from media.managers.media_versions.media_version_manager import MediaVersionManager
from media.managers.media_versions.media_version_determiner import determine_allowed_versions

class Command(BaseCommand):
    help = "Enqueue tasks to process additional media item versions using the centralized manager."

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

    def missing_versions(self, media_item, allowed_versions):
        """
        Given a media item and a list of allowed version types,
        returns a list of version types that are missing on that item.
        """
        existing = set(media_item.versions.values_list('version_type', flat=True))
        return [v for v in allowed_versions if v not in existing]

    def handle(self, *args, **options):
        regenerate = options.get('regenerate', False)
        media_item_id = options.get('media_item_id')

        if media_item_id:
            try:
                media_item = MediaItem.objects.get(id=media_item_id)
                allowed_versions = determine_allowed_versions(media_item)
                if not regenerate:
                    missing = self.missing_versions(media_item, allowed_versions)
                else:
                    missing = allowed_versions
                if missing:
                    mvm = MediaVersionManager(media_item_id)
                    mvm.process_versions(regenerate=regenerate, allowed_versions=missing)
                    self.stdout.write(self.style.SUCCESS(
                        f"Queued processing for MediaItem {media_item_id} for missing versions: {missing}."
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"MediaItem {media_item_id} already has all required versions."
                    ))
            except MediaItem.DoesNotExist:
                raise CommandError(f"MediaItem with ID {media_item_id} does not exist.")
        else:
            qs = MediaItem.objects.filter(status=MediaItem.PENDING_MODERATION)
            processed, skipped = 0, 0
            for item in qs:
                allowed_versions = determine_allowed_versions(item)
                if not regenerate:
                    missing = self.missing_versions(item, allowed_versions)
                else:
                    missing = allowed_versions
                if missing:
                    mvm = MediaVersionManager(item.id)
                    mvm.process_versions(regenerate=regenerate, allowed_versions=missing)
                    processed += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Queued processing for MediaItem {item.id} for missing versions: {missing}."
                    ))
                else:
                    skipped += 1
                    self.stdout.write(self.style.WARNING(
                        f"MediaItem {item.id} already has all required versions; skipping."
                    ))
            self.stdout.write(self.style.SUCCESS(
                f"Queued processing for {processed} items; {skipped} items were skipped."
            ))
