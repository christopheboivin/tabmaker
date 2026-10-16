"""CLI behaviour that doesn't need the AI models."""

import pytest

from tabmaker import cli


@pytest.fixture
def run_cli(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("TABMAKER_WORK", str(tmp_path / "work"))

    def run(*args):
        try:
            cli.main(list(args))
        except SystemExit as exc:
            code = exc.code or 0
        else:
            code = 0
        return code, capsys.readouterr().out

    return run


def test_home_screen_shows_status_and_commands(run_cli):
    code, out = run_cli()
    assert code == 0
    assert "TabMaker" in out and "Project:" in out and "tabmaker dev selftest" in out
    assert "none yet" in out


def test_status_command(run_cli):
    code, out = run_cli("status")
    assert code == 0 and "Project:" in out


def test_shortcut_reports_missing_file(run_cli):
    code, out = run_cli("no_such_song.mp3")
    assert code != 0


def test_songs_listed_on_home(run_cli, tmp_path):
    from tabmaker.settings import RunSettings

    song = tmp_path / "work" / "my_song"
    RunSettings(source="x.mp3", start=10).save(song / "run.toml", {"date": "2026-10-16 20:00"})
    (song / "tab.txt").write_text("tab", encoding="utf-8")
    _, out = run_cli()
    assert "my_song" in out and "2026-10-16 20:00" in out
