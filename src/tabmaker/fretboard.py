"""The fretboard as a pitch map: tunings, note names, and where each pitch can be played."""

import re
from dataclasses import dataclass

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLATS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}


def note_name(pitch: int) -> str:
    """MIDI pitch → scientific pitch name: 40 → 'E2', 60 → 'C4'."""
    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def parse_note(name: str) -> int:
    """Scientific pitch name → MIDI pitch: 'E2' → 40, 'Eb4' → 63."""
    m = re.fullmatch(r"([A-Ga-g])([#b]?)(-?\d+)", name.strip())
    if not m:
        raise ValueError(f"not a note name: {name!r} (expected something like E2, F#3, Bb2)")
    letter = m[1].upper() + m[2]
    letter = _FLATS.get(letter, letter)
    if letter not in NOTE_NAMES:  # e.g. Cb, Fb, E#
        raise ValueError(f"unsupported note name: {name!r}")
    return NOTE_NAMES.index(letter) + 12 * (int(m[3]) + 1)


@dataclass(frozen=True)
class Tuning:
    name: str
    strings: tuple[int, ...]  # open-string MIDI pitches, lowest string first
    max_fret: int = 22

    @property
    def lowest(self) -> int:
        return min(self.strings)

    @property
    def highest(self) -> int:
        return max(self.strings) + self.max_fret

    def positions(self, pitch: int) -> list[tuple[int, int]]:
        """Every (string, fret) where this pitch can be played, lowest fret first."""
        found = [
            (s, pitch - open_pitch)
            for s, open_pitch in enumerate(self.strings)
            if 0 <= pitch - open_pitch <= self.max_fret
        ]
        return sorted(found, key=lambda sf: (sf[1], sf[0]))

    def label(self, string: int) -> str:
        """Tab line label. By convention the top string is lower-case when it shares the
        bottom string's letter (e vs E in standard tuning)."""
        name = NOTE_NAMES[self.strings[string] % 12]
        lowest_name = NOTE_NAMES[self.strings[0] % 12]
        if string == len(self.strings) - 1 and name == lowest_name:
            return name.lower()
        return name

    def describe(self) -> str:
        return f"{self.name} ({' '.join(note_name(p) for p in self.strings)})"


STANDARD = Tuning("standard", (40, 45, 50, 55, 59, 64))
TUNINGS = {STANDARD.name: STANDARD}  # presets and custom tunings arrive in M5.2


def get_tuning(name: str) -> Tuning:
    try:
        return TUNINGS[name]
    except KeyError:
        known = ", ".join(TUNINGS)
        raise ValueError(f"unknown tuning {name!r} (available: {known})") from None
