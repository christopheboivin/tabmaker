"""Command line: `tabmaker <song>` for players, `tabmaker dev …` for developer tools."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from tabmaker import home, plan
from tabmaker.audio import parse_time
from tabmaker.settings import FILE as SETTINGS_FILE
from tabmaker.settings import RunSettings
from tabmaker.workdir import song_dir as default_song_dir
from tabmaker.workdir import work_root

console = Console()

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    rich_markup_mode="rich",
    help="Turns a song recording into guitar tab + chord sheets.\n\n"
    "Shortcut: [bold]tabmaker song.mp3[/] is the same as [bold]tabmaker make song.mp3[/].\n\n"
    "Run [bold]tabmaker[/] with no arguments for the home screen.",
)
dev = typer.Typer(help="Developer tools: installation checks and self-test.")
app.add_typer(dev, name="dev")


def _time_option(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return parse_time(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from None


def _resolve(target: str) -> tuple[RunSettings, Path]:
    """A target is an audio file, a song folder (work/<song>), or a song folder name."""
    path = Path(target)
    if not path.exists() and (work_root() / target).is_dir():
        path = work_root() / target
    if path.is_dir():
        settings_file = path / SETTINGS_FILE
        if not settings_file.is_file():
            raise typer.BadParameter(f"{path} is a folder but has no {SETTINGS_FILE}")
        return RunSettings.load(settings_file), path
    if not path.is_file():
        raise typer.BadParameter(f"file not found: {target}")
    folder = default_song_dir(path)
    saved = folder / SETTINGS_FILE
    if saved.is_file():
        settings = RunSettings.load(saved)
        if Path(settings.source).resolve() == path.resolve():
            return settings, folder
        console.print(
            f"[yellow]⚠[/] {folder} was made from {settings.source}; starting fresh for {path}."
        )
    return RunSettings(source=str(path.resolve())), folder


@app.command(
    epilog="Examples:\n\n"
    "  tabmaker make song.mp3\n\n"
    "  tabmaker song.mp3 --start 1:05 --end 1:40\n\n"
    "  tabmaker work/song          (re-run with the saved settings)\n\n"
    "  tabmaker song.mp3 --whole   (forget a saved range)"
)
def make(
    target: str = typer.Argument(
        ..., help="An audio file (MP3/WAV/FLAC…) or a song folder like work/<song>."
    ),
    start: str | None = typer.Option(None, help="Start time (m:ss), e.g. 1:05. Saved."),
    end: str | None = typer.Option(None, help="End time (m:ss), e.g. 1:40. Saved."),
    whole: bool = typer.Option(False, "--whole", help="Process the whole song again."),
    tuning: str | None = typer.Option(None, help="Tuning (only 'standard' until M5). Saved."),
):
    """Make or update the sheet for a song: work/<song>/tab.txt."""
    from tabmaker import pipeline  # heavy imports only when needed

    settings, folder = _resolve(target)
    if whole:
        settings.start = settings.end = None
    if start is not None:
        settings.start = _time_option(start)
    if end is not None:
        settings.end = _time_option(end)
    if tuning is not None:
        settings.tuning = tuning
    console.print(f"[bold]{Path(settings.source).name}[/] · {settings.range_text()} · {folder}")
    try:
        pipeline.run(settings, folder, console)
    except ValueError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1) from None


@app.command()
def status():
    """Where the project stands: current milestone and next task (from PLAN.md)."""
    home.show_status(console)


@app.command()
def guide():
    """Show the user guide (docs/USER-GUIDE.md)."""
    path = plan.find_file("docs/USER-GUIDE.md")
    if path is None:
        console.print("docs/USER-GUIDE.md not found: run this from the project folder.")
        raise typer.Exit(1)
    console.print(Markdown(path.read_text(encoding="utf-8")))
    console.print(f"\n(file: {path})")


@dev.command()
def doctor():
    """Check Python, audio libraries and the AI models (downloads them on the first run)."""
    from tabmaker import doctor as doctor_module

    if not doctor_module.run(console):
        raise typer.Exit(1)


@dev.command()
def selftest(
    keep: Path | None = typer.Option(None, help="Keep the self-test output in this folder."),
):
    """Run the whole pipeline on a built-in synthetic clip and check the results."""
    from tabmaker import selftest as selftest_module

    if not selftest_module.run(console, keep):
        raise typer.Exit(1)


COMMANDS = {"make", "status", "guide", "dev"}


def main(argv: list[str] | None = None) -> None:
    for stream in (sys.stdout, sys.stderr):  # pipes on Windows default to cp1252
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:] if argv is None else argv
    if not args:
        home.show_home(console)
        return
    if args[0] not in COMMANDS and not args[0].startswith("-"):
        args = ["make", *args]  # `tabmaker song.mp3` shortcut
    app(args=args, prog_name="tabmaker")
