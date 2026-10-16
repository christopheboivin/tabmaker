import numpy as np
import pytest

from tabmaker import audio, synth
from tabmaker.settings import RunSettings, last_run
from tabmaker.workdir import slug


def test_parse_and_format_time():
    assert audio.parse_time("1:05") == 65
    assert audio.parse_time("65") == 65
    assert audio.parse_time("1:05.5") == 65.5
    assert audio.parse_time("1:02:03") == 3723
    assert audio.format_time(65.9) == "1:05"
    with pytest.raises(ValueError):
        audio.parse_time("abc")


def test_settings_round_trip_with_windows_path(tmp_path):
    s = RunSettings(source=r"C:\Users\me\Music\My Song.mp3", start=65.5, end=100.0)
    path = tmp_path / "run.toml"
    s.save(path, last_run={"date": "2026-10-16 20:00", "version": "0.1.0"})
    assert RunSettings.load(path) == s
    assert 'start = "1:05.5"' in path.read_text(encoding="utf-8")
    assert last_run(path)["version"] == "0.1.0"
    assert s.range_text() == "1:05.5–1:40"
    assert RunSettings(source="x").range_text() == "whole song"


def test_slug():
    assert slug(audio.Path("My Song (Live).mp3")) == "my_song_live"
    assert slug(audio.Path("!!!.wav")) == "song"


def test_save_and_load_audio_with_trim(tmp_path):
    sr = 8000
    stereo = np.stack([np.linspace(-0.5, 0.5, sr * 2)] * 2).astype(np.float32)
    path = tmp_path / "x.wav"
    audio.save(path, stereo, sr)
    data, got_sr = audio.load(path, start=0.5, end=1.5)
    assert got_sr == sr and data.shape == (2, sr)


def test_synth_clip_is_deterministic():
    a, b = synth.test_clip(), synth.test_clip()
    assert np.array_equal(a.mix, b.mix)
    assert a.mix.shape[0] == 2 and len(a.notes) == len(synth.RIFF)
    assert np.abs(a.mix).max() <= 1.0
