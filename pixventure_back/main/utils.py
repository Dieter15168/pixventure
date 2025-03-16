# core/utils/slug_utils.py

from django.utils.text import slugify
import random
import string

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

def random_alphanumeric_string(length=10):
    """
    Generate a random alphanumeric string of the specified length.

    Parameters:
        length (int): The length of the generated string.

    Returns:
        str: A random alphanumeric string.
    """
    if length <= 0:
        raise ValueError("Length must be a positive integer.")

    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))