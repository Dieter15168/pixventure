from django.db import models


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
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('term_type', 'slug'),)

    def __str__(self):
        return f"{self.get_term_type_display()}: {self.name}"