"""Stage 2: detect notes in the guitar stem with Spotify's basic-pitch
(see docs/03-transcription.md, arriving in M3)."""

import contextlib
import io
import json
import logging
import os
import warnings
from pathlib import Path

from tabmaker.models import Note


def _quiet_tensorflow() -> None:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    warnings.filterwarnings("ignore", module="basic_pitch")
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")  # from resampy
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("root").setLevel(logging.ERROR)


def transcribe(audio_path: Path):
    """Return (notes sorted by start, pretty_midi.PrettyMIDI) for an audio file."""
    _quiet_tensorflow()
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    with contextlib.redirect_stdout(io.StringIO()):  # basic-pitch prints "Predicting MIDI…"
        _, midi, events = predict(str(audio_path), ICASSP_2022_MODEL_PATH)
    notes = sorted(
        Note(start=float(s), end=float(e), pitch=int(p), confidence=float(a))
        for s, e, p, a, _bends in events
    )
    return notes, midi


def save_notes(notes: list[Note], midi, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    midi.write(str(out_dir / "notes.mid"))
    data = [
        {
            "start": round(n.start, 4),
            "end": round(n.end, 4),
            "pitch": n.pitch,
            "confidence": round(n.confidence, 3),
        }
        for n in notes
    ]
    (out_dir / "notes.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def load_notes(path: Path) -> list[Note]:
    return [Note(**d) for d in json.loads(path.read_text(encoding="utf-8"))]
