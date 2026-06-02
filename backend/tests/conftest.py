import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parent / "setpilot_test.db"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["SETPILOT_DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
