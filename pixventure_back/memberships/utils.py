def check_if_user_is_paying(user):
    # Query user memberships or do a cached property
    if user.is_authenticated:
        return user.memberships.filter(is_active=True).exists()
    else:
        return False