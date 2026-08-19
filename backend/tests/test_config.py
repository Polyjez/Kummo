"""Settings validation.

`cookie_secure` defaults to False so that plain-HTTP local development works, which
makes a TLS deployment that forgets to set it the dangerous case: it would ship the
session and refresh tokens without the Secure flag and say nothing.
"""

import pytest
from pydantic import ValidationError

from kummo.config import Settings

REQUIRED = {
    "supabase_url": "https://project.supabase.co",
    "supabase_api_key": "anon-key",
    "database_url": "postgresql+asyncpg://user:pw@localhost/kummo",
}


def test_https_without_secure_cookies_is_refused():
    with pytest.raises(ValidationError, match="COOKIE_SECURE"):
        Settings(**REQUIRED, app_base_url="https://kummo.de", cookie_secure=False)


def test_https_with_secure_cookies_is_accepted():
    settings = Settings(**REQUIRED, app_base_url="https://kummo.de", cookie_secure=True)

    assert settings.cookie_secure is True


def test_plain_http_may_leave_cookies_insecure():
    """Local development has no TLS to require."""
    settings = Settings(
        **REQUIRED, app_base_url="http://localhost:8000", cookie_secure=False
    )

    assert settings.cookie_secure is False
