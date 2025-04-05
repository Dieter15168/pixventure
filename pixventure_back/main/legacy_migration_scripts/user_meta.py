from django.contrib.auth import get_user_model
from django.db import connections, transaction
from accounts.models import UserProfile
from memberships.models import MembershipPlan, UserMembership

User = get_user_model()

def migrate_user_meta():
    print("→ Migrating user meta and memberships...")

    # Ensure MembershipPlan entries exist
    month_plan, _ = MembershipPlan.objects.using('default').get_or_create(
        name='Month',
        defaults={'duration_days': 30, 'price': 10.00, 'currency': 'USD'}
    )
    year_plan, _ = MembershipPlan.objects.using('default').get_or_create(
        name='Year',
        defaults={'duration_days': 365, 'price': 100.00, 'currency': 'USD'}
    )

    # Load user meta from legacy DB
    with connections['legacy'].cursor() as cursor:
        cursor.execute("""
            SELECT last_visit, is_banned, ban_reason, likes_counter, 
                   is_extension_of_user_id, balance, is_active_paid_member, 
                   membership_type, membership_active_until, user_rating 
            FROM scgapp_user_meta;
        """)
        rows = cursor.fetchall()

    created_profiles = 0
    created_memberships = 0

    with transaction.atomic(using='default'):
        for row in rows:
            legacy_user_id = row[4]
            if not legacy_user_id:
                continue

            try:
                user = User.objects.using('default').get(id=legacy_user_id)
            except User.DoesNotExist:
                print(f"  Skipping user_meta: no matching user with ID {legacy_user_id}")
                continue

            # Create or update UserProfile
            profile, created = UserProfile.objects.using('default').update_or_create(
                user=user,
                defaults={'likes_counter': row[3]}
            )
            if created:
                created_profiles += 1

            # Create a membership if active
            if row[6]:  # is_active_paid_member == True
                plan = None
                if row[7] == 1:
                    plan = month_plan
                elif row[7] == 2:
                    plan = year_plan

                if plan:
                    # Prevent duplicates by checking if a membership exists for this user+plan+end_date
                    membership_exists = UserMembership.objects.using('default').filter(
                        user=user,
                        plan=plan,
                        end_date=row[8]
                    ).exists()

                    if not membership_exists:
                        UserMembership.objects.using('default').create(
                            user=user,
                            plan=plan,
                            end_date=row[8],
                            is_active=True
                        )
                        created_memberships += 1

    print(f"✓ Migrated {created_profiles} user profiles.")
    print(f"✓ Created {created_memberships} active memberships.")
