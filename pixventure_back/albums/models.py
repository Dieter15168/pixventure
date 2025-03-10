from django.db import models
from django.contrib.auth.models import User
from media.models import MediaItem

class Album(models.Model):
    """
    Represents a collection of Posts and/or MediaItems in a defined order, 
    with lifecycle management via a status field.
    """

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Possible statuses: 
    # - PENDING_MODRATION: waiting for the moderator's action
    # - PUBLIC: visible to all
    # - PRIVATE: only owner or authorized users can view
    # - DELETED: soft delete, can be restored or archived from this state
    # - ARCHIVED: no longer visible in normal listings
    PENDING_MODERATION = 0
    PUBLIC = 1
    PRIVATE = 2
    DELETED = 3
    ARCHIVED = 4

    ALBUM_STATUS_CHOICES = [
        (PENDING_MODERATION, 'Pending moderation'),
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (DELETED, 'Deleted'),
        (ARCHIVED, 'Archived'),
    ]

    status = models.IntegerField(
        choices=ALBUM_STATUS_CHOICES,
        default=PRIVATE,
        null=False,
        blank=False
    )

    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024)

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='albums'
    )
    
    # The featured item is used as a thumbnail or cover image
    featured_item = models.ForeignKey(MediaItem, null=True, blank=True,
                                      on_delete=models.PROTECT, related_name='+')


    # Whether to display the album creator's name/avatar to other users
    show_creator_to_others = models.BooleanField(default=True)

    # The total number of likes on the album
    likes_counter = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def update_featured_item(self):
        """
        Update the album's featured item.
        
        If a current featured item exists, check:
         1. If any media element references it.
         2. If any post element has a post whose featured_item matches it.
         
        If either is true, do nothing.
        Otherwise, update the featured item by selecting the first available media element;
        if none, then the first post element's featured item; if neither exists, clear it.
        """
        if self.featured_item:
            # Check if a media element in the album still references it.
            media_ref = self.album_elements.filter(
                element_type=AlbumElement.MEDIA_TYPE,
                element_media=self.featured_item
            ).exists()
            if media_ref:
                return  # It is still valid.

            # Check if a post element in the album provides this featured item.
            post_ref = self.album_elements.filter(
                element_type=AlbumElement.POST_TYPE,
                element_post__featured_item=self.featured_item
            ).exists()
            if post_ref:
                return  # Still valid as derived from a post.
        
        # Otherwise, try to set a new featured item.
        new_media = self.album_elements.filter(
            element_type=AlbumElement.MEDIA_TYPE,
            element_media__isnull=False
        ).order_by('position').first()
        if new_media:
            self.featured_item = new_media.element_media
            self.save(update_fields=['featured_item'])
            return

        post_element = self.album_elements.filter(
            element_type=AlbumElement.POST_TYPE,
            element_post__isnull=False
        ).order_by('position').first()
        if post_element and post_element.element_post.featured_item:
            self.featured_item = post_element.element_post.featured_item
            self.save(update_fields=['featured_item'])
            return

        # No suitable featured item found.
        self.featured_item = None
        self.save(update_fields=['featured_item'])


class AlbumElement(models.Model):
    """
    Through-model storing the items (Posts or MediaItems) that belong to an Album,
    with a specific order and timestamps.
    """
    # This model references either a Post or a MediaItem. 
    # We use 'element_type' to distinguish which type of content is being referenced.

    POST_TYPE = 1
    MEDIA_TYPE = 2
    ELEMENT_TYPE_CHOICES = [
        (POST_TYPE, 'Post'),
        (MEDIA_TYPE, 'MediaItem'),
    ]

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='album_elements'
    )

    element_type = models.PositiveSmallIntegerField(choices=ELEMENT_TYPE_CHOICES)
    element_post = models.ForeignKey(
        'posts.Post',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    element_media = models.ForeignKey(
        'media.MediaItem',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    # This field controls the ordering of items in the album
    position = models.PositiveIntegerField(default=0)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)  # replaces added_date
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        # Return a human-readable reference indicating which type of item is linked
        if self.element_type == self.POST_TYPE and self.element_post:
            return f"{self.album} -> Post: {self.element_post} (pos: {self.position})"
        elif self.element_type == self.MEDIA_TYPE and self.element_media:
            return f"{self.album} -> Media: {self.element_media} (pos: {self.position})"
        return f"{self.album} -> Unknown element"
