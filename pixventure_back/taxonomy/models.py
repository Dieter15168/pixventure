from django.db import models

class Tag(models.Model):
    """
    Represents a keyword/tag used to label media items or posts.
    For example: 'funny', 'travel', 'summer'.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Represents a content category (e.g. 'Nature', 'Sports').
    Separated from Tag for clarity, to enforce a single primary category on Posts.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name