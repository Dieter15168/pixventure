# core/utils/slug_utils.py

from django.utils.text import slugify

def generate_unique_slug(model_class, name, max_length=50):
    """
    Returns a unique slug for the given name, ensuring there's no conflict
    with existing records of the given `model_class`.
    """
    base_slug = slugify(name)[:max_length] or "post"
    slug = base_slug
    counter = 1

    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
