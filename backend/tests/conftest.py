import os

# Default for unit tests; integration/conftest.py overrides when running integration only.
os.environ.setdefault("USE_MEMORY_STORE", "true")
