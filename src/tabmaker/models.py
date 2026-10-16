"""Core data types shared by all pipeline stages."""

from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Note:
    """A detected note: start/end in seconds, MIDI pitch, and the detector's confidence (0..1)."""

    start: float
    end: float
    pitch: int
    confidence: float = 1.0


@dataclass(frozen=True)
class TabNote:
    """A note placed on the fretboard. Strings are numbered from the lowest one (0 = low E)."""

    note: Note
    string: int
    fret: int


@dataclass
class Column:
    """Notes struck together, printed as one column of the tab."""

    time: float
    notes: list[TabNote] = field(default_factory=list)
