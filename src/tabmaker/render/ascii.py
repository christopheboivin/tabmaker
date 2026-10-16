"""Plain-text tab (see docs/07-tab-notation.md, arriving in M5).

M1 layout: one block per ~4 seconds, starting with its [m:ss] time, high string on top.
Silence between notes shows as extra dashes (about one per 1/8 s, capped), so the spacing
roughly follows the rhythm until real bars arrive in M4."""

from tabmaker.audio import format_time
from tabmaker.fretboard import Tuning
from tabmaker.models import Column

LINE_SECONDS = 4.0
DASH_SECONDS = 0.125
MAX_GAP = 6


def render_tab(
    columns: list[Column],
    tuning: Tuning,
    time_offset: float = 0.0,
    line_seconds: float = LINE_SECONDS,
) -> str:
    blocks = []
    for chunk in _chunks(columns, line_seconds):
        rows = _rows(chunk, tuning)
        blocks.append("\n".join([f"[{format_time(time_offset + chunk[0].time)}]", *rows]))
    return "\n\n".join(blocks) + "\n"


def _chunks(columns: list[Column], line_seconds: float) -> list[list[Column]]:
    chunks: dict[int, list[Column]] = {}
    for col in sorted(columns, key=lambda c: c.time):
        chunks.setdefault(int(col.time // line_seconds), []).append(col)
    return [chunks[k] for k in sorted(chunks)]


def _rows(chunk: list[Column], tuning: Tuning) -> list[str]:
    n = len(tuning.strings)
    cells: list[list[str]] = [[] for _ in range(n)]
    previous = None
    for col in chunk:
        gap = 1 if previous is None else 1 + min(MAX_GAP, int((col.time - previous) / DASH_SECONDS))
        frets = {t.string: str(t.fret) for t in col.notes}
        width = max(len(f) for f in frets.values())
        for s in range(n):
            cells[s].append("-" * gap + frets.get(s, "").ljust(width, "-"))
        previous = col.time
    label_width = max(len(tuning.label(s)) for s in range(n))
    return [
        f"{tuning.label(s).ljust(label_width)}|{''.join(cells[s])}-|" for s in reversed(range(n))
    ]
