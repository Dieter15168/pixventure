from django.core.management.base import BaseCommand
from main.models import Setting

DEFAULT_SETTINGS = {
    "watermarked_preview_quality": 80,
    "full_watermarked_version_quality": 90,
    "blurred_thumbnail_quality": 70,
    "blurred_preview_quality": 70,
    "thumbnail_size": 300,   # Maximum dimension (width/height) for thumbnails
    "preview_size": 800,     # Maximum dimension for previews
}

class Command(BaseCommand):
    help = "Populate the Setting model with default values if they don't exist."

    def handle(self, *args, **kwargs):
        for key, value in DEFAULT_SETTINGS.items():
            setting, created = Setting.objects.get_or_create(key=key, defaults={"value": value})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added: {key} = {value}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {key} = {setting.value}"))
