# media/management/commands/compute_missing_phashes.py
from django.core.management.base import BaseCommand
from media.models import MediaItemVersion, HashType
from media.jobs.dispatcher import TaskDispatcher

class Command(BaseCommand):
    help = "Enqueue tasks to compute phashes for original versions of media items that don't have them."

    def handle(self, *args, **options):
        # Get or create the hash type for phash
        phash_type, _ = HashType.objects.get_or_create(name="phash")
        
        # Filter for original versions
        versions = MediaItemVersion.objects.filter(version_type=MediaItemVersion.ORIGINAL)
        dispatched_count = 0
        
        for version in versions:
            # Check if a phash already exists for this version
            if not version.hashes.filter(hash_type=phash_type).exists():
                TaskDispatcher.dispatch_fuzzy_hash(media_item_version_id=version.id, hash_type="phash")
                dispatched_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Dispatched phash computation tasks for {dispatched_count} media item versions."
        ))
