"""Stage 1: isolate the guitar from the full mix with Demucs (see docs/02-source-separation.md)."""

from pathlib import Path

import numpy as np

from tabmaker import audio

MODEL = "htdemucs_6s"  # the Demucs variant with a dedicated guitar stem
CACHE_FILE = "cache_key.txt"


def cache_key(source: Path, start: float | None, end: float | None) -> str:
    return f"{audio.file_hash(source)}|{start}|{end}|{MODEL}"


def cached_stems(stem_dir: Path, key: str) -> dict[str, Path] | None:
    """The stems from a previous run with the same input, or None."""
    key_file = stem_dir / CACHE_FILE
    if not key_file.exists() or key_file.read_text(encoding="utf-8") != key:
        return None
    stems = {p.stem: p for p in stem_dir.glob("*.wav")}
    return stems if "guitar" in stems else None


def separate(mix: np.ndarray, sr: int, stem_dir: Path, key: str, progress: bool = True):
    """Split a (channels, samples) mix into stems (drums, bass, other, vocals, guitar, piano),
    save each as a WAV in stem_dir, and return {stem name: path}."""
    import soxr
    import torch
    from demucs.apply import apply_model
    from demucs.pretrained import get_model

    model = get_model(MODEL)
    model.eval()
    if mix.shape[0] == 1:  # Demucs expects stereo
        mix = np.repeat(mix, 2, axis=0)
    if sr != model.samplerate:
        mix = soxr.resample(mix.T, sr, model.samplerate).T
    wav = torch.from_numpy(np.ascontiguousarray(mix, dtype=np.float32))
    # Demucs was trained on normalized audio: scale in, separate, scale back.
    ref = wav.mean(0)
    mean, std = ref.mean(), ref.std() + 1e-8
    device = "cuda" if torch.cuda.is_available() else "cpu"
    with torch.no_grad():
        sources = apply_model(
            model,
            ((wav - mean) / std)[None],
            device=device,
            split=True,
            overlap=0.25,
            progress=progress,
        )[0]
    sources = sources * std + mean

    stem_dir.mkdir(parents=True, exist_ok=True)
    stems = {}
    for name, stem in zip(model.sources, sources, strict=True):
        stems[name] = stem_dir / f"{name}.wav"
        audio.save(stems[name], stem.cpu().numpy(), model.samplerate)
    (stem_dir / CACHE_FILE).write_text(key, encoding="utf-8")
    return stems
