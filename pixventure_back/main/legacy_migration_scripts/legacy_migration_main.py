from .users import migrate_users
from .user_meta import migrate_user_meta
from .terms import migrate_terms
from .media_migration import migrate_media_items
from .posts_migration import migrate_posts
from .albums_migration import migrate_albums
from .likes_migration import migrate_likes

def run_legacy_migration():
    print("Starting legacy data migration...")

    migrate_users()
    migrate_user_meta()
    migrate_terms()
    migrate_media_items()
    migrate_posts()
    migrate_albums()
    migrate_likes()

    print("Legacy data migration completed.")
