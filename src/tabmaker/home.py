"""The home screen (`tabmaker` with no arguments) and `tabmaker status`: everything needed to
pick the project back up after a break."""

import re

from rich.console import Console
from rich.table import Table

from tabmaker import plan, settings, workdir

PITCH = "[bold]TabMaker[/]: turns a song recording into guitar tab + chord sheets."

COMMANDS = [
    ("tabmaker <file.mp3>", "make or update a sheet (also: tabmaker work/<song> to re-run)"),
    ("tabmaker guide", "the user guide"),
    ("tabmaker status", "project progress (from PLAN.md)"),
    ("tabmaker dev doctor", "check the installation"),
    ("tabmaker dev selftest", "run the whole pipeline on a built-in clip"),
    ("tabmaker --help", "all commands and options"),
]


def show_status(console: Console) -> None:
    p = plan.load()
    if p is None:
        console.print("Project status: PLAN.md not found (run from the project folder).")
        return
    current = p.current()
    if current is None:
        console.print("Project: all milestones done.")
        return
    done = sum(1 for m in p.milestones.values() if m.status == "DONE")
    console.print(
        f"Project: [bold]{current.id} {current.title}[/] ({current.status})"
        f" · {done}/{len(p.milestones)} milestones done"
    )
    task = current.next_task()
    if task:
        text = re.sub(r"[*`]", "", task.text)
        console.print(f"Next task: [bold]{task.id}[/] {text[:90]}{'…' if len(text) > 90 else ''}")


def show_songs(console: Console) -> None:
    root = workdir.work_root()
    songs = sorted(p for p in root.glob("*/") if (p / settings.FILE).is_file())
    if not songs:
        console.print("Your songs: none yet. Try [bold]tabmaker path/to/song.mp3[/]")
        return
    table = Table(title=f"Your songs ({root})", title_justify="left", box=None, pad_edge=False)
    for col in ("song", "sheet", "last run", "range", "tuning"):
        table.add_column(col)
    for song in songs:
        try:
            s = settings.RunSettings.load(song / settings.FILE)
            rng, tuning = s.range_text(), s.tuning
        except (OSError, ValueError, TypeError):
            rng, tuning = "?", "?"
        sheet = "[green]✓[/]" if (song / "tab.txt").is_file() else "[red]✗[/]"
        when = settings.last_run(song / settings.FILE).get("date", "never finished")
        table.add_row(song.name, sheet, when, rng, tuning)
    console.print(table)


def latest_changes(count: int = 2) -> list[str]:
    path = plan.find_file("CHANGELOG.md")
    if path is None:
        return []
    headings = re.findall(r"^## (.+)$", path.read_text(encoding="utf-8"), flags=re.M)
    return headings[:count]


def show_home(console: Console) -> None:
    console.print(PITCH)
    console.print()
    show_status(console)
    console.print()
    show_songs(console)
    console.print()
    console.print("[bold]Commands[/]")
    for cmd, what in COMMANDS:
        console.print(f"  [cyan]{cmd:<24}[/] {what}")
    changes = latest_changes()
    if changes:
        console.print()
        console.print("[bold]What's new[/] (CHANGELOG.md): " + " · ".join(changes))
