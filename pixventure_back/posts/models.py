from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from taxonomy.models import Term
from media.models import MediaItem

class Post(models.Model):
    """
    Represents a Post, which can include multiple MediaItems in a defined order
    and can be tagged, categorized, etc.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    DRAFT = 0
    PENDING_MODERATION = 1
    PUBLISHED = 2
    PRIVATE = 3
    REJECTED = 4
    DELETED = 5
    ARCHIVED = 6

    ITEM_STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING_MODERATION, 'Pending moderation'),
        (PUBLISHED, 'Published'),
        (PRIVATE, 'Private'),
        (REJECTED, 'Rejected by moderation'),
        (DELETED, 'Deleted'),
        (ARCHIVED, 'Archived'),
    ]

    status = models.IntegerField(choices=ITEM_STATUS_CHOICES, default=1, null=True, blank=True)
    
    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT,
                                        related_name='posts')


    # Category: enforce a single main category
    main_category = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name='posts_with_main_category',
        limit_choices_to={'term_type': 2},  # 2 => CATEGORY
    )
    
    # Categories:
    categories = models.ManyToManyField(
        Term,
        blank=True,
        related_name='posts_with_category',
        limit_choices_to={'term_type': 2},  # 2 => CATEGORY
    )
    
    # Tags:
    tags = models.ManyToManyField(
        Term,
        blank=True,
        related_name='posts_with_tag',
        limit_choices_to={'term_type': 1},  # 1 => TAG
    )
    
    # The featured item is used as a thumbnail or cover image
    featured_item = models.ForeignKey(MediaItem, null=True, blank=True,
                                      on_delete=models.PROTECT, related_name='+')

    likes_counter = models.IntegerField(default=0)
    
    # Featured posts will appear in a special feed on the main page
    is_featured_post = models.BooleanField(default=False)
    
    # Blurred posts will have all content blurred for non-paying users
    is_blurred = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class PostMedia(models.Model):
    """
    Through-model connecting Post to MediaItems in a specific order.
    Allows storing additional details, e.g. position or timestamps.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_media_links')
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='post_links')

    position = models.PositiveIntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('post', 'media_item'),)
        ordering = ['position']

    def __str__(self):
        return f"{self.post} -> {self.media_item} (pos: {self.position})"