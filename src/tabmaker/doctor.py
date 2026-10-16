"""`tabmaker dev doctor`: checks the installation and loads each model once (which also
downloads it on the first run)."""

import platform
import shutil
import sys
from collections.abc import Callable

from rich.console import Console
from rich.table import Table

OK, WARN, FAIL = "[green]ok[/]", "[yellow]warning[/]", "[red]FAIL[/]"


def _python():
    v = sys.version_info
    status = OK if (v.major, v.minor) == (3, 11) else FAIL
    return status, f"{platform.python_version()} (the project needs 3.11)"


def _soundfile():
    import soundfile as sf

    mp3 = "MP3" in sf.available_formats()
    detail = f"libsndfile {sf.__libsndfile_version__}, MP3 {'yes' if mp3 else 'no'}"
    return (OK if mp3 else WARN), detail


def _ffmpeg():
    path = shutil.which("ffmpeg")
    if path:
        return OK, path
    return WARN, "not found: only needed for M4A/AAC files (MP3/WAV/FLAC work without it)"


def _torch():
    import torch

    gpu = torch.cuda.is_available()
    return OK, f"torch {torch.__version__}, " + ("GPU available" if gpu else "CPU only")


def _demucs():
    from demucs.pretrained import get_model

    from tabmaker.separate import MODEL

    model = get_model(MODEL)
    return OK, f"{MODEL} loaded, stems: {', '.join(model.sources)}"


def _basic_pitch():
    from tabmaker.transcribe import _quiet_tensorflow

    _quiet_tensorflow()
    import tensorflow as tf
    from basic_pitch import ICASSP_2022_MODEL_PATH

    tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))
    return OK, f"model loaded (TensorFlow {tf.__version__})"


def _beat_this():
    from beat_this.inference import Audio2Beats

    Audio2Beats(checkpoint_path="final0", device="cpu", dbn=False)
    return OK, "final0 checkpoint loaded (used from M4)"


def _work_dir():
    from tabmaker.workdir import work_root

    root = work_root()
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ".write_test"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink()
    free = shutil.disk_usage(root).free / 2**30
    return (OK if free > 2 else WARN), f"{root} (writable, {free:.0f} GB free)"


CHECKS: list[tuple[str, Callable]] = [
    ("Python", _python),
    ("Audio files (soundfile)", _soundfile),
    ("ffmpeg (optional)", _ffmpeg),
    ("PyTorch", _torch),
    ("Guitar isolation (Demucs)", _demucs),
    ("Note detection (basic-pitch)", _basic_pitch),
    ("Beat tracking (beat_this)", _beat_this),
    ("Work folder", _work_dir),
]


def run(console: Console) -> bool:
    table = Table(title="TabMaker doctor", title_justify="left")
    for col in ("check", "status", "details"):
        table.add_column(col)
    healthy = True
    with console.status("Checking (the first run downloads the models)…") as status:
        for name, check in CHECKS:
            status.update(f"Checking {name}…")
            try:
                result, detail = check()
            except Exception as exc:  # report every failure, whatever it is
                result, detail = FAIL, f"{type(exc).__name__}: {exc}"
            healthy &= result != FAIL
            table.add_row(name, result, detail)
    console.print(table)
    console.print("All good." if healthy else "[red]Something is broken.[/] See docs/DEV-GUIDE.md.")
    return healthy
