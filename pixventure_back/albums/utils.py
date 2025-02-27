# albums/utils.py

import uuid
from django.utils.text import slugify
from .models import Album

def generate_unique_slug(name, max_length=50):
    """
    Returns a unique slug for the given name, 
    ensuring there's no conflict with existing Albums.
    """
    base_slug = slugify(name)[:max_length]
    if not base_slug:
        base_slug = "album"

    slug = base_slug
    counter = 1

    while Album.objects.filter(slug=slug).exists():
        # Increase counter until we find a free slug
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
