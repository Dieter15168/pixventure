import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from PIL import Image
from media.models import MediaItemVersion

class Command(BaseCommand):
    help = 'Populates missing width, height, and file_size metadata for MediaItemVersion instances.'

    def handle(self, *args, **options):
        versions = MediaItemVersion.objects.filter(
            Q(width__isnull=True) | Q(height__isnull=True) | Q(file_size__isnull=True),
            file__isnull=False
        )

        total = versions.count()
        updated_count = 0

        self.stdout.write(f'Found {total} MediaItemVersion(s) with missing metadata.')

        for version in versions:
            file_path = version.file.path
            metadata_updated = False

            # Check file existence
            if not os.path.exists(file_path):
                self.stderr.write(f'File not found: {file_path} (MediaItemVersion id: {version.id})')
                continue

            # Populate file_size
            if version.file_size is None:
                version.file_size = os.path.getsize(file_path)
                metadata_updated = True
                self.stdout.write(f'Set file_size for version id {version.id}: {version.file_size} bytes.')

            # Populate width and height (assuming image files)
            if version.width is None or version.height is None:
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        version.width = width
                        version.height = height
                        metadata_updated = True
                        self.stdout.write(
                            f'Set dimensions for version id {version.id}: {width}x{height}.'
                        )
                except Exception as e:
                    self.stderr.write(
                        f'Error reading image dimensions for file {file_path}: {str(e)}'
                    )
                    continue  # Skip saving if image can't be read

            if metadata_updated:
                version.save()
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Updated metadata for {updated_count}/{total} MediaItemVersion(s).'
        ))
