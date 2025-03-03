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
    

class Term(models.Model):
    """
    A unified model for both "tags" and "categories".
    term_type indicates whether this term is acting as a 'tag' or 'category'.
    """
    TAG = 1
    CATEGORY = 2
    TERM_TYPE_CHOICES = [
        (TAG, 'Tag'),
        (CATEGORY, 'Category'),
    ]

    term_type = models.IntegerField(choices=TERM_TYPE_CHOICES)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        unique_together = (('term_type', 'slug'),)

    def __str__(self):
        return f"{self.get_term_type_display()}: {self.name}"