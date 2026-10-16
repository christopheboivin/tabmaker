"""Tiny synthesizer for test clips: Karplus-Strong plucked strings plus simple drums.

Used by `tabmaker dev selftest` and the tests, so the project never needs copyrighted audio
to check that the pipeline works.
"""

from dataclasses import dataclass

import numpy as np

SR = 44100


def midi_to_hz(pitch: float) -> float:
    return 440.0 * 2 ** ((pitch - 69) / 12)


def pluck(pitch: int, duration: float, sr: int = SR, decay: float = 0.996, seed: int = 0):
    """Karplus-Strong: a burst of noise circulating in a delay line that is as long as one
    period of the note. Averaging neighbouring samples on each pass damps the high harmonics,
    which is what makes it sound like a plucked string."""
    rng = np.random.default_rng(seed)
    # The averaging filter adds half a sample of delay, so shorten the line to stay in tune.
    period = max(2, round(sr / midi_to_hz(pitch) - 0.5))
    buf = rng.uniform(-1.0, 1.0, period)
    out = np.empty(int(duration * sr), dtype=np.float32)
    for i in range(len(out)):
        j = i % period
        out[i] = buf[j]
        buf[j] = decay * 0.5 * (buf[j] + buf[(j + 1) % period])
    fade = min(len(out), int(0.01 * sr))  # avoid a click when the note is cut
    out[len(out) - fade :] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return out


def kick(sr: int = SR) -> np.ndarray:
    t = np.arange(int(0.15 * sr)) / sr
    freq = 40 + 50 * np.exp(-t * 30)  # pitch sweeps down, like a kick drum
    return (np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-t * 25)).astype(np.float32)


def hihat(sr: int = SR, seed: int = 1) -> np.ndarray:
    n = int(0.04 * sr)
    noise = np.diff(np.random.default_rng(seed).uniform(-1, 1, n + 1))  # crude high-pass
    return (noise * np.exp(-np.arange(n) / sr * 120)).astype(np.float32)


@dataclass(frozen=True)
class TestClip:
    guitar: np.ndarray  # mono guitar only
    mix: np.ndarray  # stereo (2, samples): guitar + drums
    notes: list[tuple[float, int]]  # (onset seconds, MIDI pitch) actually played
    sr: int = SR


# An original E minor pentatonic exercise, one note per eighth at 120 BPM.
RIFF = [52, 55, 57, 59, 62, 59, 57, 55, 52, 55, 57, 62, 64, 62, 59, 57]


def test_clip(bpm: float = 120.0, sr: int = SR) -> TestClip:
    eighth = 60.0 / bpm / 2
    length = int((len(RIFF) * eighth + 1.0) * sr)
    guitar = np.zeros(length, dtype=np.float32)
    drums = np.zeros(length, dtype=np.float32)
    notes = []
    for k, pitch in enumerate(RIFF):
        onset = k * eighth
        tone = pluck(pitch, eighth if k < len(RIFF) - 1 else 1.0, sr, seed=k)
        i = int(onset * sr)
        guitar[i : i + len(tone)] += tone[: length - i]
        notes.append((onset, pitch))
        hit = kick(sr) if k % 2 == 0 else hihat(sr) * 0.3
        drums[i : i + len(hit)] += hit[: length - i]
    guitar *= 0.6 / max(1e-9, np.abs(guitar).max())
    mix = guitar + 0.5 * drums
    mix *= 0.9 / max(1e-9, np.abs(mix).max())
    return TestClip(guitar=guitar, mix=np.stack([mix, mix]), notes=notes, sr=sr)
