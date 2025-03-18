# taxonomy/utils.py
from taxonomy.models import Term

def get_mandatory_category(category_qs):
    """
    Ensures we always have a non-null category.
    1) If category_qs exists, return the first one.
    2) Otherwise, fallback to the first category in DB.
    3) If still none, raise ValueError.
    """
    # If user provided valid categories, use the first
    if category_qs.exists():
        return category_qs.first()

    # Otherwise fallback to first available category
    fallback_cat = Term.objects.filter(term_type=Term.CATEGORY).first()
    if fallback_cat is not None:
        return fallback_cat

    # If no category at all in DB, raise
    raise ValueError("No category available in system (cannot set main_category).")
