from __future__ import annotations

import os
import sys
from pathlib import Path


def load_dotenv(path: str = ".env") -> None:
    # Web builds shouldn't rely on env/.env.
    if sys.platform == "emscripten":
        return
    p = Path(path)
    if not p.exists() or not p.is_file():
        return

    try:
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            os.environ.setdefault(key, value)
    except Exception:
        return
