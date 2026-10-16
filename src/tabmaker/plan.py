"""Reads PLAN.md, so the tool can show where the project stands (home screen, `status`)."""

import re
from dataclasses import dataclass, field
from pathlib import Path

STATES = ("NOT STARTED", "IN PROGRESS", "DONE", "DROPPED")
TABLE_ROW = re.compile(r"^\|\s*(M\d+|L)\s*\|.*\|\s*([A-Z ]+?)\s*\|\s*$")
HEADER = re.compile(r"^### (M\d+|L): (.+) · ([A-Z ]+?)\s*$")
TASK = re.compile(r"^- \[(.)\] ((M\d+|L)\.\d+) (.*)$")
OVERALL = re.compile(r"\*\*Overall status: ([A-Z ]+?)\*\*")


@dataclass
class Task:
    id: str
    mark: str  # ' ' not started, '~' in progress, 'x' done, '-' dropped
    text: str
    section: str | None  # the milestone whose section lists it


@dataclass
class Milestone:
    id: str
    title: str
    status: str
    tasks: list[Task] = field(default_factory=list)

    def next_task(self) -> Task | None:
        for mark in ("~", " "):
            for task in self.tasks:
                if task.mark == mark:
                    return task
        return None


@dataclass
class Plan:
    overall: str | None
    table: dict[str, str]  # milestone id → status, from the status overview
    milestones: dict[str, Milestone]  # from the "### M<N>: …" sections, in order
    tasks: list[Task]

    def current(self) -> Milestone | None:
        """The milestone being worked on, else the next one to start."""
        for wanted in ("IN PROGRESS", "NOT STARTED"):
            for m in self.milestones.values():
                if m.status == wanted and m.id != "L":
                    return m
        return None


def parse(text: str) -> Plan:
    table, milestones, tasks = {}, {}, []
    current = None
    for line in text.splitlines():
        if m := TABLE_ROW.match(line):
            table[m[1]] = m[2]
        elif m := HEADER.match(line):
            current = Milestone(id=m[1], title=m[2], status=m[3])
            milestones[current.id] = current
        elif m := TASK.match(line):
            task = Task(id=m[2], mark=m[1], text=m[4], section=current.id if current else None)
            tasks.append(task)
            if current:
                current.tasks.append(task)
        elif line.startswith("## "):
            current = None  # tasks only count inside a milestone section
    overall = OVERALL.search(text)
    return Plan(overall[1] if overall else None, table, milestones, tasks)


def find_file(relative: str) -> Path | None:
    """Find a repo file (PLAN.md, docs/…) from the current folder or the installed package."""
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    for start in starts:
        for folder in (start, *start.parents):
            if (folder / relative).is_file():
                return folder / relative
    return None


def load() -> Plan | None:
    path = find_file("PLAN.md")
    return parse(path.read_text(encoding="utf-8")) if path else None


def summary() -> str:
    """One line for sheet headers, e.g. 'M1 End-to-end skeleton… (IN PROGRESS)'."""
    plan = load()
    current = plan.current() if plan else None
    return f"{current.id} {current.title} ({current.status})" if current else "unknown"
