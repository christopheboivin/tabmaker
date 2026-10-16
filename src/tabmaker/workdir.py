"""Where per-song output lives: work/<song>/ (override the root with TABMAKER_WORK)."""

import os
import re
from pathlib import Path


def work_root() -> Path:
    return Path(os.environ.get("TABMAKER_WORK", "work")).resolve()


def slug(source: Path) -> str:
    """'My Song (Live).mp3' → 'my_song_live'."""
    return re.sub(r"[^a-z0-9]+", "_", source.stem.lower()).strip("_") or "song"


def song_dir(source: Path) -> Path:
    return work_root() / slug(source)
