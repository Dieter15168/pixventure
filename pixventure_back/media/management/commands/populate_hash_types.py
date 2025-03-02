# management/commands/populate_hash_types.py
from django.core.management.base import BaseCommand
from media.models import HashType

class Command(BaseCommand):
    help = 'Populate the HashType model with predefined hash types'

    def handle(self, *args, **kwargs):
        hash_types = [
            {'name': 'sha256', 'description': 'SHA256 hash for file integrity'},
            {'name': 'p-hash', 'description': 'Perceptual hash for content similarity'},
            {'name': 'd-hash', 'description': 'Difference hash for content similarity'},
            {'name': 'a-hash', 'description': 'Average hash for media comparison'},
            {'name': 'w-hash', 'description': 'Wavelet hash for visual media content'}
        ]

        for hash_type in hash_types:
            obj, created = HashType.objects.get_or_create(
                name=hash_type['name'],
                defaults={'description': hash_type['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created hash type {obj.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Hash type {obj.name} already exists"))
