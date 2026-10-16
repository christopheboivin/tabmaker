"""Reading/writing audio and parsing m:ss times."""

import hashlib
import re
from pathlib import Path

import numpy as np
import soundfile as sf


def parse_time(text: str) -> float:
    """'1:05' → 65.0, '65' → 65.0, '1:05.5' → 65.5, '1:02:03' → 3723.0."""
    if not re.fullmatch(r"\d+(\.\d+)?(:\d{1,2}(\.\d+)?){0,2}", text.strip()):
        raise ValueError(f"not a time: {text!r} (use m:ss, e.g. 1:05)")
    seconds = 0.0
    for part in text.strip().split(":"):
        seconds = seconds * 60 + float(part)
    return seconds


def format_time(seconds: float) -> str:
    """65.4 → '1:05'."""
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def load(path: Path, start: float | None = None, end: float | None = None):
    """Load audio as float32 (channels, samples) plus its sample rate, optionally trimmed.

    libsndfile reads WAV/FLAC/OGG/MP3 directly; other formats (M4A…) go through librosa,
    which needs ffmpeg on the PATH."""
    try:
        info = sf.info(str(path))
    except sf.LibsndfileError:
        return _load_with_librosa(path, start, end)
    sr = info.samplerate
    first = int((start or 0) * sr)
    last = int(end * sr) if end is not None else None
    data, sr = sf.read(str(path), start=first, stop=last, dtype="float32", always_2d=True)
    return np.ascontiguousarray(data.T), sr


def _load_with_librosa(path: Path, start: float | None, end: float | None):
    import librosa

    offset = start or 0.0
    duration = None if end is None else max(0.0, end - offset)
    data, sr = librosa.load(str(path), sr=None, mono=False, offset=offset, duration=duration)
    return np.atleast_2d(data).astype(np.float32), sr


def save(path: Path, audio: np.ndarray, sr: int) -> None:
    """Save (channels, samples) or mono audio as 16-bit WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.clip(audio.T if audio.ndim == 2 else audio, -1.0, 1.0)
    sf.write(str(path), data, sr, subtype="PCM_16")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]
