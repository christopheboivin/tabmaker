from tabmaker.fingering import group_columns, naive_fingering, out_of_range
from tabmaker.fretboard import STANDARD
from tabmaker.models import Note
from tabmaker.render.ascii import render_tab


def n(start, pitch):
    return Note(start=start, end=start + 0.2, pitch=pitch)


def test_group_columns_uses_onset_window():
    groups = group_columns([n(0.0, 40), n(0.01, 47), n(0.5, 52)])
    assert [[x.pitch for x in g] for g in groups] == [[40, 47], [52]]


def test_naive_fingering_picks_lowest_fret():
    columns, unplaced = naive_fingering([n(0.0, 60)], STANDARD)
    assert unplaced == []
    (tab,) = columns[0].notes
    assert (tab.string, tab.fret) == (4, 1)  # C4 on the B string, fret 1


def test_chord_notes_never_share_a_string():
    # E2 + E3 + B3 struck together: each must land on its own string
    columns, unplaced = naive_fingering([n(0, 40), n(0, 52), n(0, 59)], STANDARD)
    strings = [t.string for t in columns[0].notes]
    assert unplaced == [] and len(set(strings)) == 3


def test_out_of_range_notes_are_reported_not_placed():
    notes = [n(0, 38), n(0.5, 40), n(1.0, 100)]
    assert [x.pitch for x in out_of_range(notes, STANDARD)] == [38, 100]
    columns, unplaced = naive_fingering(notes, STANDARD)
    assert [x.pitch for x in unplaced] == [38, 100]
    assert len(columns) == 1


def test_render_simple_line():
    columns, _ = naive_fingering([n(0.0, 64), n(0.25, 67), n(0.5, 59)], STANDARD)
    text = render_tab(columns, STANDARD, time_offset=65.0)
    assert text == (
        "[1:05]\n"
        "e|-0---3-----|\n"
        "B|---------0-|\n"
        "G|-----------|\n"
        "D|-----------|\n"
        "A|-----------|\n"
        "E|-----------|\n"
    )


def test_render_splits_lines_by_time():
    columns, _ = naive_fingering([n(0.0, 64), n(4.5, 64)], STANDARD)
    text = render_tab(columns, STANDARD)
    assert text.count("e|") == 2 and "[0:00]" in text and "[0:04]" in text


def test_two_digit_frets_keep_columns_aligned():
    columns, _ = naive_fingering([n(0, 76), n(0, 59)], STANDARD)  # e12 + B0
    rows = render_tab(columns, STANDARD).splitlines()[1:]
    assert len({len(r) for r in rows}) == 1
