from django.contrib.auth import get_user_model
from django.db import connections, transaction

User = get_user_model()

def migrate_users():
    print("→ Migrating users...")

    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT id, password, last_login, is_superuser, username, 
                   first_name, last_name, email, is_staff, is_active, date_joined 
            FROM auth_user;
        """)
        users = cursor.fetchall()

    with transaction.atomic(using='default'):
        for row in users:
            obj, created = User.objects.using('default').update_or_create(
                id=row[0],  # match by ID to avoid duplicates
                defaults={
                    'password': row[1],
                    'last_login': row[2],
                    'is_superuser': row[3],
                    'username': row[4],
                    'first_name': row[5],
                    'last_name': row[6],
                    'email': row[7],
                    'is_staff': row[8],
                    'is_active': row[9],
                    'date_joined': row[10],
                }
            )
            action = "Created" if created else "Updated"
            # print(f"  {action} user: {obj.username} (id={obj.id})")

    print(f"✓ {len(users)} users processed.")
