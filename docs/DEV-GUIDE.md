# TabMaker developer guide

## Resuming after a break (start here)
1. `git switch main && git pull`, then `gh pr list`: an open PR is a milestone waiting for your review (merge it before starting the next one).
   `git log --oneline -15`: commits are prefixed with task IDs (`M3.2: …`), so this is the recent history of the plan.
2. Open [PLAN.md](../PLAN.md): the status table shows the current milestone, and its first `[ ]` task is the next thing to do.
3. `uv sync && uv run pytest` checks the environment still builds and tests pass. Later, `uv run tabmaker dev selftest` *(M1.9)* also runs the pipeline end to end.
4. With Claude: open this folder and say "continue the project". `CLAUDE.md` tells it to read `PLAN.md` and follow its rules.

## Setup
- Requirements: [uv](https://docs.astral.sh/uv/), git. Python 3.11 is installed by uv; the project is pinned to `>=3.11,<3.12` for ML dependency compatibility.
- `uv sync` creates `.venv` from `uv.lock`. The lock file is committed, so the exact same versions come back months later.
- Fallback: if a native ML dependency won't install on Windows, use WSL Ubuntu (`wsl.exe -d Ubuntu`) with the same commands, and record the switch in the PLAN.md Decision log.

### Known Windows quirk (uv Python install)
On this machine, `uv sync` downloaded Python 3.11 but failed with `Missing expected target directory for Python minor version link`. Workaround: point uv at the downloaded interpreter directly:
```bash
uv sync --python "C:/Users/chris/AppData/Roaming/uv/python/cpython-3.11.17-windows-x86_64-none/python.exe"
```
Once `.venv` exists, plain `uv sync` / `uv run` reuse it.

## Everyday commands
```bash
uv run pytest
```
```bash
uv run tabmaker
```
Developer tools will live under `uv run tabmaker dev …` (doctor, selftest, eval, tune, learn); see PLAN.md for when each lands.

## Rules (summary of PLAN.md "How this plan is maintained")
- Work task by task. Mark `[~]` while working and `[x]` when done; commit messages start with the task ID.
- **Definition of done**:
  - tests pass;
  - PLAN.md is updated;
  - for user-visible changes, USER-GUIDE.md and CHANGELOG.md are updated;
  - for concepts, the tutorial in `docs/` is updated.
- Design changes go in the PLAN.md Decision log, with the Reference design kept in sync.
- `tests/test_plan.py` fails if PLAN.md's status table and task checkboxes disagree.
- **One branch + one PR per milestone**: branch `m<N>-<slug>` from an up-to-date `main`, PR titled `M<N>: <title>`, merged by you after review. Never commit milestone work directly to `main`.
- Push only once a set of related changes is complete (each push triggers CI).

## Architecture
```
song.mp3 ─→ separate ─→ guitar stem ─┬─→ transcribe notes ─┐
    └───→ full mix ─→ beats & bars ──┤                     ├─→ segmenter: each bar = tab | chords
                                     └─→ chroma per beat ──┘
  tab bars   ─→ fingering (Viterbi)                          ─┐
  chord bars ─→ chord recognition (Viterbi) ─→ voicing + strum ┴─→ render work/<song>/tab.txt
```

| Module (`src/tabmaker/`) | Role | Milestone |
|---|---|---|
| `cli.py`, `home.py` | commands, home screen / status | M1 |
| `models.py` | Note, TabNote, ChordSpan, Bar, Segment | M1 |
| `separate.py` | Demucs stems, cache, stereo split | M1, M3 |
| `transcribe.py` | basic-pitch notes + cleanup | M1, M3 |
| `rhythm.py` | beats, tempo map, quantization, strums | M4 |
| `fretboard.py`, `fingering.py` | tunings, positions, Viterbi | M1, M5 |
| `chords.py`, `voicings.py`, `segmenter.py` | chord mode | M6 |
| `review.py` | alternatives, review.txt, learning | M7 |
| `play.py` | playback, slow-down, synth | M3, M5 |
| `reference.py`, `align.py`, `evaluate.py`, `tune.py` | benchmark & improvement | M2, M8 |
| `render/ascii.py`, `render/gp5.py` | output | M1, M9 |
| `selftest.py` | end-to-end self check | M1 |

Folders that are **not committed** (personal and copyrighted data): `work/` (per-song output), `bench/` (benchmark songs + references), `feedback/` (review choices).

The full design lives in PLAN.md → "Reference design".
