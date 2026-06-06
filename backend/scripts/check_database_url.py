from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import SplitResult, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import get_database_url, normalize_database_url


def get_database_dialect(database_url: str) -> str:
    scheme = urlsplit(normalize_database_url(database_url)).scheme
    return scheme.split("+", 1)[0] if scheme else "unknown"


def has_credentials(parts: SplitResult) -> bool:
    return bool(parts.username or parts.password)


def build_database_url_report(database_url: str | None = None) -> list[str]:
    resolved_url = normalize_database_url(database_url) if database_url is not None else get_database_url()
    parts = urlsplit(resolved_url)
    dialect = get_database_dialect(resolved_url)

    if dialect == "sqlite":
        return [
            "Database dialect: sqlite",
            "Host: local-file",
            "Credentials: none",
        ]

    host_status = "masked" if parts.hostname else "not configured"
    credential_status = "masked" if has_credentials(parts) else "none"
    driver = parts.scheme.split("+", 1)[1] if "+" in parts.scheme else "default"

    return [
        f"Database dialect: {dialect}",
        f"Driver: {driver}",
        f"Host: {host_status}",
        f"Credentials: {credential_status}",
    ]


def main() -> None:
    for line in build_database_url_report():
        print(line)


if __name__ == "__main__":
    main()
