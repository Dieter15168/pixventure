from django.db import connections, transaction
from taxonomy.models import Term as NewTerm

# Old legacy term types to new types mapping
LEGACY_CATEGORY = 1
LEGACY_TAG = 2

NEW_TAG = NewTerm.TAG
NEW_CATEGORY = NewTerm.CATEGORY

TERM_TYPE_MAPPING = {
    LEGACY_CATEGORY: NEW_CATEGORY,
    LEGACY_TAG: NEW_TAG,
}

def migrate_terms():
    print("→ Migrating Terms...")

    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT name, slug, type FROM scgapp_term;
        """)
        terms = cursor.fetchall()

    created_count = 0
    updated_count = 0

    with transaction.atomic(using='default'):
        for row in terms:
            name, slug, legacy_type = row

            new_term_type = TERM_TYPE_MAPPING.get(legacy_type)
            if not new_term_type:
                print(f"  ⚠️ Unknown term type ({legacy_type}) for '{name}', skipping.")
                continue

            term, created = NewTerm.objects.using('default').update_or_create(
                term_type=new_term_type,
                slug=slug,
                defaults={
                    'name': name,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

    print(f"✓ Created: {created_count}, Updated: {updated_count} terms.")
