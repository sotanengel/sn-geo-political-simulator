import os

os.environ["USE_MEMORY_STORE"] = "false"
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault(
    "DATABASE_URL", "postgresql://geo:geo@localhost:5432/geopolitical"
)
