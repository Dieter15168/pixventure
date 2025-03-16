# posts/management/commands/publish_approved_posts.py
from django.core.management.base import BaseCommand
from posts.models import Post
from posts.managers.post_publication_manager import PostPublicationManager

class Command(BaseCommand):
    help = "Publish all posts that are approved and ready for publication."

    def handle(self, *args, **options):
        approved_posts = Post.objects.filter(status=Post.APPROVED)
        published_count = 0
        skipped_count = 0

        for post in approved_posts:
            result = PostPublicationManager.publish_post(post.id)
            if result:
                published_count += 1
                self.stdout.write(self.style.SUCCESS(f"Published Post ID: {post.id}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Skipped Post ID: {post.id}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Publication process completed: {published_count} published, {skipped_count} skipped."
        ))
