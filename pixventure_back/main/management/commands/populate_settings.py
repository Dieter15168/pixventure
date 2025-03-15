from django.core.management.base import BaseCommand
from main.models import Setting
from main.default_settings_config import DEFAULT_SETTINGS

class Command(BaseCommand):
    help = "Populate the Setting model with default values if they don't exist."

    def handle(self, *args, **kwargs):
        for key, value in DEFAULT_SETTINGS.items():
            setting, created = Setting.objects.get_or_create(key=key, defaults={"value": value})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added: {key} = {value}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {key} = {setting.value}"))
