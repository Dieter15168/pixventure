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
    # - ARCHIVED: no longer visible in normal listings
    PENDING_MODRATION = 0
    PUBLIC = 1
    PRIVATE = 2
    ARCHIVED = 3

    ALBUM_STATUS_CHOICES = [
        (PENDING_MODRATION, 'Pending moderation'),
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
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
