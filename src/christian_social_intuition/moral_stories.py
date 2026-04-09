from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

DEFAULT_FULL_DATA_URL = (
    "https://huggingface.co/datasets/demelin/moral_stories/resolve/main/data/moral_stories_full.jsonl"
)


def fetch_moral_stories(
    output_path: str | Path,
    *,
    url: str = DEFAULT_FULL_DATA_URL,
    force: bool = False,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return path
    with urlopen(url, timeout=30) as response:
        payload = response.read()
    path.write_bytes(payload)
    return path


def iter_moral_stories(path: str | Path) -> Iterable[dict]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_moral_stories(path: str | Path) -> list[dict]:
    return list(iter_moral_stories(path))
