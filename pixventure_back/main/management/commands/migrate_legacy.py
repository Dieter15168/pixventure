from django.core.management.base import BaseCommand
from main.legacy_migration_scripts.legacy_migration_main import run_legacy_migration

class Command(BaseCommand):
    help = 'Migrate data from legacy PostgreSQL DB to new schema'

    def handle(self, *args, **options):
        run_legacy_migration()
