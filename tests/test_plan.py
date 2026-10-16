"""Keeps PLAN.md internally consistent, so its status can be trusted after a long break."""

import re
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parent.parent / "PLAN.md"

STATES = {"NOT STARTED", "IN PROGRESS", "DONE", "DROPPED"}
# Milestone ids: M0..M99 or L (later/ideas).
TABLE_ROW = re.compile(r"^\|\s*(M\d+|L)\s*\|.*\|\s*([A-Z ]+?)\s*\|\s*$")
HEADER = re.compile(r"^### (M\d+|L): .+ · ([A-Z ]+?)\s*$")
TASK = re.compile(r"^- \[(.)\] ((M\d+|L)\.\d+) ")
OVERALL = re.compile(r"\*\*Overall status: ([A-Z ]+?)\*\*")


def _parse():
    text = PLAN.read_text(encoding="utf-8")
    table, headers, tasks = {}, {}, []
    current = None
    for line in text.splitlines():
        if m := TABLE_ROW.match(line):
            table[m[1]] = m[2]
        elif m := HEADER.match(line):
            current = m[1]
            headers[current] = m[2]
        elif m := TASK.match(line):
            tasks.append((current, m[1], m[2], m[3]))
        elif line.startswith("## "):
            current = None  # tasks only count inside a milestone section
    overall = OVERALL.search(text)
    return table, headers, tasks, overall[1] if overall else None


TABLE, HEADERS, TASKS, OVERALL_STATUS = _parse()


def test_plan_has_milestones():
    assert TABLE and HEADERS and TASKS


def test_status_values_are_valid():
    for mid, state in {**TABLE, **HEADERS}.items():
        assert state in STATES, f"{mid}: unknown status {state!r}"


def test_table_matches_headers():
    assert TABLE == HEADERS, "status table and milestone headers disagree"


def test_task_marks_are_valid():
    for _, mark, tid, _ in TASKS:
        assert mark in " ~x-", f"{tid}: unknown mark [{mark}]"


def test_task_ids_unique_and_in_their_milestone():
    ids = [tid for _, _, tid, _ in TASKS]
    assert len(ids) == len(set(ids)), "duplicate task ids"
    for section, _, tid, prefix in TASKS:
        assert section == prefix, f"{tid} is listed under {section}"


@pytest.mark.parametrize("mid", sorted(HEADERS))
def test_milestone_status_matches_tasks(mid):
    marks = {mark for section, mark, _, _ in TASKS if section == mid}
    state = HEADERS[mid]
    if state == "DONE":
        assert marks <= {"x", "-"}, f"{mid} is DONE but has open tasks"
    elif state == "NOT STARTED":
        assert marks <= {" ", "-"}, f"{mid} has started tasks: set it to IN PROGRESS"
    elif state == "IN PROGRESS":
        assert marks & {"x", "~"}, f"{mid} is IN PROGRESS but no task is started"


def test_overall_status_consistent():
    assert OVERALL_STATUS in STATES
    states = set(TABLE.values())
    if states <= {"NOT STARTED"}:
        assert OVERALL_STATUS == "NOT STARTED"
    else:
        assert OVERALL_STATUS != "NOT STARTED", "a milestone has started: update the overall status"
