"""`tabmaker dev selftest`: proves the whole pipeline still works, using a synthetic clip
(no copyrighted audio needed)."""

import tempfile
import time
from pathlib import Path

from rich.console import Console

from tabmaker import audio, pipeline, synth
from tabmaker.settings import RunSettings
from tabmaker.transcribe import transcribe

ONSET_TOLERANCE = 0.08  # seconds
MIN_RECALL = 0.8


def note_recall(expected: list[tuple[float, int]], found) -> float:
    """Share of expected (onset, pitch) notes found with the same pitch near the same time."""
    hits = sum(
        any(n.pitch == pitch and abs(n.start - onset) <= ONSET_TOLERANCE for n in found)
        for onset, pitch in expected
    )
    return hits / len(expected)


def run(console: Console, keep: Path | None = None) -> bool:
    clip = synth.test_clip()
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        folder = keep or Path(tmp)
        folder.mkdir(parents=True, exist_ok=True)

        # 1. Note detection on the clean synthetic guitar (checks basic-pitch on its own).
        t = time.perf_counter()
        guitar_path = folder / "selftest_guitar.wav"
        audio.save(guitar_path, clip.guitar, clip.sr)
        notes, _ = transcribe(guitar_path)
        recall = note_recall(clip.notes, notes)
        passed = recall >= MIN_RECALL
        ok &= passed
        console.print(
            f"{'[green]✓[/]' if passed else '[red]✗[/]'} Note detection on a clean guitar:"
            f" found {recall:.0%} of the {len(clip.notes)} notes (need {MIN_RECALL:.0%})"
            f" · {time.perf_counter() - t:.0f}s"
        )

        # 2. Whole pipeline on guitar + drums, twice (the second run must reuse the stems).
        t = time.perf_counter()
        mix_path = folder / "selftest_mix.wav"
        audio.save(mix_path, clip.mix, clip.sr)
        song_dir = folder / "work" / "selftest_mix"
        settings = RunSettings(source=str(mix_path))
        quiet = Console(quiet=True)
        try:
            first = pipeline.run(settings, song_dir, quiet)
            second = pipeline.run(RunSettings.load(song_dir / "run.toml"), song_dir, quiet)
            tab = first.tab_path.read_text(encoding="utf-8")
            checks = {
                "tab.txt has tab lines": "|" in tab and any(c.isdigit() for c in tab),
                "notes were placed on the fretboard": first.placed > 0,
                "re-run reused the cached stems": second.stems_cached,
            }
        except Exception as exc:  # any crash is a failed self-test
            checks = {f"pipeline crashed: {type(exc).__name__}: {exc}": False}
        for name, passed in checks.items():
            ok &= passed
            console.print(f"{'[green]✓[/]' if passed else '[red]✗[/]'} Pipeline: {name}")
        console.print(f"  (whole pipeline, two runs: {time.perf_counter() - t:.0f}s)")
        if keep:
            console.print(f"  Output kept in {song_dir}")
    console.print("Self-test passed." if ok else "[red]Self-test FAILED.[/]")
    return ok
