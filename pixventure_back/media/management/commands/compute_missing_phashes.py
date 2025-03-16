# media/management/commands/compute_missing_phashes.py
from django.core.management.base import BaseCommand
from media.models import MediaItemVersion, HashType
from media.managers.hashing.hashing_manager import HashingManager

class Command(BaseCommand):
    help = "Enqueue tasks to compute phashes for original versions of image media items that don't have them."

    def handle(self, *args, **options):
        phash_type, _ = HashType.objects.get_or_create(name="phash")
        versions = MediaItemVersion.objects.filter(
            version_type=MediaItemVersion.ORIGINAL,
            media_item__media_type__exact=1  # assuming PHOTO is represented as 1
        )
        dispatched_count = 0
        
        for version in versions:
            if not version.hashes.filter(hash_type=phash_type).exists():
                HashingManager.process_fuzzy_hash(version.id, hash_type="phash")
                dispatched_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Dispatched phash computation tasks for {dispatched_count} media item versions."
        ))
