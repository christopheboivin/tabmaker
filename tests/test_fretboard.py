import pytest

from tabmaker.fretboard import STANDARD, get_tuning, note_name, parse_note


def test_note_names_round_trip():
    assert note_name(40) == "E2"
    assert note_name(60) == "C4"
    assert parse_note("E2") == 40
    assert parse_note("Eb4") == parse_note("D#4") == 63
    for pitch in range(28, 100):
        assert parse_note(note_name(pitch)) == pitch


def test_parse_note_rejects_garbage():
    with pytest.raises(ValueError):
        parse_note("H2")


def test_middle_c_has_five_positions_lowest_fret_first():
    # strings: 0=E2 1=A2 2=D3 3=G3 4=B3 5=E4
    assert STANDARD.positions(60) == [(4, 1), (3, 5), (2, 10), (1, 15), (0, 20)]


def test_range():
    assert STANDARD.lowest == 40  # open low E
    assert STANDARD.highest == 64 + 22
    assert STANDARD.positions(39) == []
    assert STANDARD.positions(87) == []


def test_labels_and_description():
    assert [STANDARD.label(s) for s in range(6)] == ["E", "A", "D", "G", "B", "e"]
    assert STANDARD.describe() == "standard (E2 A2 D3 G3 B3 E4)"


def test_unknown_tuning():
    assert get_tuning("standard") is STANDARD
    with pytest.raises(ValueError, match="unknown tuning"):
        get_tuning("dadgad")
