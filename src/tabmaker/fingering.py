"""Stage 3: choose a string and fret for every note (see docs/05-fingering.md, arriving in M5).

M1 uses the naive rule: the lowest fret available. M5 replaces it with a Viterbi search that
keeps the hand in one place."""

from tabmaker.fretboard import Tuning
from tabmaker.models import Column, Note, TabNote

# Notes starting within this window are printed in the same column. M3.2 refines this
# into proper chord grouping.
COLUMN_WINDOW = 0.03


def group_columns(notes: list[Note], window: float = COLUMN_WINDOW) -> list[list[Note]]:
    groups: list[list[Note]] = []
    for note in sorted(notes):
        if groups and note.start - groups[-1][0].start <= window:
            groups[-1].append(note)
        else:
            groups.append([note])
    return groups


def naive_fingering(notes: list[Note], tuning: Tuning) -> tuple[list[Column], list[Note]]:
    """Return (tab columns, notes that could not be placed).

    A note can't be placed when it is outside the tuning's range, or when every string that
    could play it is already used in the same column."""
    columns, unplaced = [], []
    for group in group_columns(notes):
        column = Column(time=group[0].start)
        used: set[int] = set()
        for note in sorted(group, key=lambda n: -n.pitch):
            free = [(s, f) for s, f in tuning.positions(note.pitch) if s not in used]
            if not free:
                unplaced.append(note)
                continue
            string, fret = free[0]
            used.add(string)
            column.notes.append(TabNote(note=note, string=string, fret=fret))
        if column.notes:
            columns.append(column)
    return columns, unplaced


def out_of_range(notes: list[Note], tuning: Tuning) -> list[Note]:
    return [n for n in notes if not tuning.positions(n.pitch)]
