import secrets


def random_token(length: int = 48) -> str:
    """Return a URL-safe random token string."""
    return secrets.token_urlsafe(length)
