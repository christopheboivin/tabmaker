"""Per-song memory: work/<song>/run.toml keeps the settings so a re-run needs no flags."""

import json
import tomllib
from dataclasses import dataclass, fields
from pathlib import Path

from tabmaker.audio import parse_time

FILE = "run.toml"


def _time_text(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:05.2f}".rstrip("0").rstrip(".") if s % 1 else f"{int(m)}:{int(s):02d}"


@dataclass
class RunSettings:
    source: str  # absolute path of the audio file
    start: float | None = None  # seconds; None = beginning of the song
    end: float | None = None  # seconds; None = end of the song
    tuning: str = "standard"

    def range_text(self) -> str:
        if self.start is None and self.end is None:
            return "whole song"
        start = _time_text(self.start or 0)
        end = _time_text(self.end) if self.end is not None else "end"
        return f"{start}–{end}"

    def save(self, path: Path, last_run: dict[str, str] | None = None) -> None:
        lines = [
            "# TabMaker settings for this song.",
            "# `tabmaker <this folder>` re-runs with them. Options given on the command line",
            "# replace these values and are saved here. Times are m:ss.",
        ]
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            if f.name in ("start", "end"):
                value = _time_text(value)
            lines.append(f"{f.name} = {json.dumps(value)}")
        if last_run:
            lines += ["", "[last_run]"] + [f"{k} = {json.dumps(v)}" for k, v in last_run.items()]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "RunSettings":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        values = {k: v for k, v in data.items() if k in known}
        for key in ("start", "end"):
            if isinstance(values.get(key), str):
                values[key] = parse_time(values[key])
        return cls(**values)


def last_run(path: Path) -> dict[str, str]:
    """The [last_run] table of a run.toml (date, version…), or {}."""
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")).get("last_run", {})
    except (OSError, tomllib.TOMLDecodeError):
        return {}
