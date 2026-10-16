"""
Test settings: the real settings with only what tests must not touch swapped out.
"""

from .settings import *  # noqa: F401,F403

SECRET_KEY = "test-only-not-secret-padded-to-32-bytes-for-hs256"

# ponytail: SQLite in-memory, fast and no service needed. Swap for a Postgres
# service in CI if a test ever depends on Postgres-specific behaviour.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# Hashing is deliberately slow in production; MD5 makes the suite fast.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# High rates so DRF's throttle never interferes; the per-user cooldowns stored
# on the model are what the tests exercise.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {scope: "1000/min" for scope in REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]},  # noqa: F405
}

# Empty values: if a test forgets to mock the sender, the Azure client fails to
# build, the error is caught, and no email can leave the machine. Overrides
# anything a developer's local .env sets.
AZURE_EMAIL_CONNECTION_STRING = ""
AZURE_SENDER_EMAIL = ""
