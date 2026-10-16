"""Runs the stages for one song: audio → guitar stem → notes → fingering → tab.txt."""

import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rich.console import Console

from tabmaker import __version__, audio, plan, separate
from tabmaker.fingering import naive_fingering, out_of_range
from tabmaker.fretboard import get_tuning, note_name
from tabmaker.render.ascii import render_tab
from tabmaker.settings import FILE as SETTINGS_FILE
from tabmaker.settings import RunSettings
from tabmaker.transcribe import save_notes, transcribe


@dataclass
class Result:
    song_dir: Path
    tab_path: Path
    detected: int
    placed: int
    below_range: int
    above_range: int
    no_free_string: int
    stems_cached: bool
    timings: dict[str, float] = field(default_factory=dict)


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).resolve().parent,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def run(settings: RunSettings, song_dir: Path, console: Console | None = None) -> Result:
    console = console or Console()
    source = Path(settings.source)
    tuning = get_tuning(settings.tuning)
    timings: dict[str, float] = {}
    stem_dir = song_dir / "stems"
    settings.save(song_dir / SETTINGS_FILE)  # remembered even if a later stage fails

    # 1. Guitar isolation (cached: re-runs with the same audio and range skip it)
    t = time.perf_counter()
    key = separate.cache_key(source, settings.start, settings.end)
    stems = separate.cached_stems(stem_dir, key)
    cached = stems is not None
    if cached:
        console.print("[green]✓[/] Guitar isolation: reusing the stems from the last run")
    else:
        with console.status("Loading audio…"):
            mix, sr = audio.load(source, settings.start, settings.end)
        if mix.shape[1] == 0:
            raise ValueError(f"no audio to process in {settings.range_text()} of {source.name}")
        audio.save(song_dir / "mix.wav", mix, sr)
        console.print(
            f"Isolating the guitar with Demucs ({audio.format_time(mix.shape[1] / sr)} of audio)."
            " On a CPU this takes about as long as the audio itself; the first run also"
            " downloads the model."
        )
        stems = separate.separate(mix, sr, stem_dir, key, progress=not console.quiet)
        console.print("[green]✓[/] Guitar isolation")
    timings["separation"] = time.perf_counter() - t

    # 2. Note detection on the guitar stem
    t = time.perf_counter()
    with console.status("Detecting notes in the guitar stem (basic-pitch)…"):
        notes, midi = transcribe(stems["guitar"])
    save_notes(notes, midi, song_dir)
    timings["transcription"] = time.perf_counter() - t
    console.print(f"[green]✓[/] Note detection: {len(notes)} notes")

    # 3. Fingering + 4. rendering
    below = [n for n in out_of_range(notes, tuning) if n.pitch < tuning.lowest]
    above = [n for n in out_of_range(notes, tuning) if n.pitch > tuning.highest]
    columns, unplaced = naive_fingering(notes, tuning)
    placed = sum(len(c.notes) for c in columns)
    no_free = len(unplaced) - len(below) - len(above)
    if below:
        lowest = note_name(min(n.pitch for n in below))
        console.print(
            f"[yellow]⚠[/] {len(below)} notes are lower than this tuning's lowest string"
            f" ({note_name(tuning.lowest)}); the lowest one is {lowest}. If the song is tuned"
            " down (Eb, Drop D…), other tunings arrive in M5. Some may be bass bleeding into"
            " the guitar stem."
        )
    if above:
        console.print(
            f"[yellow]⚠[/] {len(above)} notes are above fret {tuning.max_fret} of the top string"
            " (probably harmonics detected as notes; M3 filters them)."
        )

    tab_path = song_dir / "tab.txt"
    header = _header(settings, song_dir, tuning, len(notes), placed, below, above, no_free)
    body = render_tab(columns, tuning, time_offset=settings.start or 0.0)
    tab_path.write_text(header + "\n" + body, encoding="utf-8")
    settings.save(
        song_dir / SETTINGS_FILE,
        last_run={
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "version": __version__,
            "notes": str(len(notes)),
        },
    )
    console.print(f"[green]✓[/] Sheet written: [bold]{tab_path}[/]")
    return Result(
        song_dir, tab_path, len(notes), placed, len(below), len(above), no_free, cached, timings
    )


def _short_path(path: Path) -> str:
    """Relative to the current folder when it's inside it (work/my_song), else absolute."""
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _header(settings, song_dir, tuning, detected, placed, below, above, no_free) -> str:
    skipped = []
    if below or above:
        skipped.append(f"{len(below) + len(above)} out of the tuning's range")
    if no_free:
        skipped.append(f"{no_free} with no free string")
    lines = [
        f"TabMaker sheet: {Path(settings.source).name}",
        f"Source:    {settings.source} ({settings.range_text()})",
        f"Made:      {datetime.now():%Y-%m-%d %H:%M} · tabmaker {__version__}"
        f" · plan {plan.summary()} · git {_git_commit()}",
        f"Settings:  tuning {tuning.describe()}",
        f"Re-run:    tabmaker {_short_path(song_dir)}",
        f"Notes:     {detected} detected, {placed} shown"
        + (f" ({', '.join(skipped)} not shown)" if skipped else ""),
        "How to read: numbers are frets, the top line is the highest string. [m:ss] is the time",
        "             where the line starts; extra dashes mean a pause. No bars yet (M4).",
        "             Positions are the lowest fret, not yet the most comfortable (M5).",
    ]
    return "\n".join(lines) + "\n"
