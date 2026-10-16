"""Keeps PLAN.md internally consistent, so its status can be trusted after a long break."""

from pathlib import Path

import pytest

from tabmaker import plan

PLAN = plan.parse((Path(__file__).resolve().parent.parent / "PLAN.md").read_text("utf-8"))
MILESTONES = PLAN.milestones


def test_plan_has_milestones():
    assert PLAN.table and MILESTONES and PLAN.tasks


def test_status_values_are_valid():
    for mid, state in PLAN.table.items():
        assert state in plan.STATES, f"{mid}: unknown status {state!r} in the status table"
    for m in MILESTONES.values():
        assert m.status in plan.STATES, f"{m.id}: unknown status {m.status!r}"


def test_table_matches_headers():
    headers = {m.id: m.status for m in MILESTONES.values()}
    assert PLAN.table == headers, "status table and milestone headers disagree"


def test_task_marks_are_valid():
    for task in PLAN.tasks:
        assert task.mark in " ~x-", f"{task.id}: unknown mark [{task.mark}]"


def test_task_ids_unique_and_in_their_milestone():
    ids = [t.id for t in PLAN.tasks]
    assert len(ids) == len(set(ids)), "duplicate task ids"
    for task in PLAN.tasks:
        assert task.section == task.id.split(".")[0], f"{task.id} is listed under {task.section}"


@pytest.mark.parametrize("mid", sorted(MILESTONES))
def test_milestone_status_matches_tasks(mid):
    m = MILESTONES[mid]
    marks = {t.mark for t in m.tasks}
    if m.status == "DONE":
        assert marks <= {"x", "-"}, f"{mid} is DONE but has open tasks"
    elif m.status == "NOT STARTED":
        assert marks <= {" ", "-"}, f"{mid} has started tasks: set it to IN PROGRESS"
    elif m.status == "IN PROGRESS":
        assert marks & {"x", "~"}, f"{mid} is IN PROGRESS but no task is started"


def test_at_most_one_task_in_progress():
    busy = [t.id for t in PLAN.tasks if t.mark == "~"]
    assert len(busy) <= 1, f"several tasks marked [~]: {busy}"


def test_overall_status_consistent():
    assert PLAN.overall in plan.STATES
    if set(PLAN.table.values()) <= {"NOT STARTED"}:
        assert PLAN.overall == "NOT STARTED"
    else:
        assert PLAN.overall != "NOT STARTED", "a milestone has started: update the overall status"


def test_current_milestone_and_next_task():
    current = PLAN.current()
    if current is not None and current.status != "DONE":
        assert current.next_task() is not None or current.status == "IN PROGRESS"
