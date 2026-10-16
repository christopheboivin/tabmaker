# TabMaker: audio → guitar tab & chord sheets

> **Living plan.** Task M0.2 copies this file into the repo as `PLAN.md`; from then on `PLAN.md` is the single source of truth.
> **Overall status: IN PROGRESS** (M1 code works on the synthetic clip · next: M1.13 guided session on a real song, then labs). Last updated: 2026-10-16.

## Coming back after a break (read this first)
The project is built so you never have to remember anything:

| You want to… | Do this | What you get |
|---|---|---|
| Know where things stand (any role) | run `tabmaker` with no arguments | home screen: what the tool does, project status + next task, your songs and their review state, the two commands, what's new |
| **Use it as a guitar player** | read `docs/USER-GUIDE.md` (or `tabmaker guide`) | step-by-step: make a sheet, read it, check by ear, review, re-run |
| Re-process a song without remembering flags | `tabmaker work/<song>` | it re-runs with the settings saved in `work/<song>/run.toml` (tuning, mode, guitar side, range) |
| Know how an old `tab.txt` was made | read its header | date, tool version, milestone, settings used |
| See what's new since last time | `CHANGELOG.md` (last entries also on the home screen) | changes in player language |
| Check nothing broke while you were away | `tabmaker dev selftest` | end-to-end run on a built-in clip + environment check |
| **Work on the code** | read `docs/DEV-GUIDE.md`, then `PLAN.md` (or `tabmaker status`) | architecture, how to run/test, the next unchecked task |
| See what's waiting for your review | `gh pr list` | open milestone PRs (one per milestone) |
| Continue with Claude | open the folder and say "continue the project" | Claude reads `CLAUDE.md` → `PLAN.md` → proposes the next task |
| Know if the tool got better | `tabmaker dev eval bench/ --history` | score trend over time |

## How this plan is maintained (rules for every session)
1. Find the current milestone in the status table, then its first unchecked task. Mark it `[~]` while working on it.
2. Each task has an ID (`M3.2`). Commit messages start with that ID (`M3.2: ghost-note filter`), so `git log` is also a history of the plan.
3. **Definition of done (every task)**:
   - tests pass, and `ruff check` + `ruff format --check` are clean;
   - the task is checked `[x]` here;
   - if users see the change: `docs/USER-GUIDE.md` is updated and an entry goes into `CHANGELOG.md`;
   - if a concept is involved: its tutorial in `docs/` is updated.
4. A milestone is `DONE` when all its tasks are `[x]` (or `[-]` with a reason) **and** its "Done when" check passes. Then update the status table and the Progress log (with eval scores from M2 on).
5. Design changes go to the **Decision log** (dated), and the Reference design is edited to match.
6. `tests/test_plan.py` keeps this file consistent; drift fails the test suite.
6b. **Learning track** (this is a learning project): every stage gets a guided session (the user runs it on a real song while Claude explains), a Jupyter lab in `labs/`, and, for key algorithms (fingering Viterbi M5, chord templates M6, quantization M4…), **"you code, I coach"**: Claude writes the scaffold and the tests, the user writes the core with hints. No large code drops without a check-in.
7. **Git workflow: one branch + one pull request per milestone.**
   - Start each milestone on a new branch from an up-to-date `main`, named `m<N>-<slug>` (e.g. `m1-skeleton`). Never commit milestone work directly to `main`.
   - Commit `PLAN.md` updates together with the code they describe, on that branch. Push only once a coherent set of tasks is complete.
   - When the milestone's "Done when" passes, open a PR titled `M<N>: <milestone title>`. Its description lists the tasks done, how they were verified, and what's left for the user to check by ear or by hand. The PR also sets the milestone to `DONE` in `PLAN.md`.
   - **CI** (`.github/workflows/ci.yml`) runs on every PR: ruff lint + format check, `uv sync --locked`, pytest, package build and CLI smoke test, on Ubuntu and Windows. A PR is merged only when CI is green.
   - The user reviews and merges. Record the PR link in the Progress log.
   - Small fixes outside any milestone also go through their own short branch + PR.

**Legend**: `[ ]` not started · `[~]` in progress · `[x]` done · `[-]` dropped (reason in the Decision log)
**Milestone states**: `NOT STARTED` · `IN PROGRESS` · `DONE` · `DROPPED`

## Status overview
| # | Milestone | Phase | Status |
|---|---|---|---|
| M0 | Bootstrap repo, plan & "don't forget" kit | setup | DONE |
| M1 | End-to-end skeleton on a real song | 1 | IN PROGRESS |
| M2 | Evaluation harness | 1 | NOT STARTED |
| M3 | Transcription quality | 1 | NOT STARTED |
| M4 | Rhythm & bars | 1 | NOT STARTED |
| M5 | Fingering (Viterbi) & tunings | 1 | NOT STARTED |
| M6 | Chord mode | 1 | NOT STARTED |
| — | **Cut line: M0, M1, M3–M6 = usable tool** | | |
| M7 | Review loop | 1 | NOT STARTED |
| M8 | Improvement loop | 1 | NOT STARTED |
| M9 | Guitar Pro 5 export | 2 | NOT STARTED |
| L | Later / ideas | — | NOT STARTED |

---

## Context
A personal **learning** project. It takes a full song recording (MP3/WAV), isolates the guitar, and outputs a plain-text sheet mixing **tab** (single-note lines, riffs) and **chords** (strummed parts: names, shapes, strum pattern). It is a Python CLI first; Guitar Pro/TuxGuitar export comes in phase 2. Standard 6-string tuning first, with the tuning built into the design so Eb/Drop D/custom tunings arrive early. Every stage gets a concept tutorial (DSP/music/ML, not Python). The project is worked on occasionally, so everything needed to resume (status, how to use it, how it works) lives in the repo and is shown by the tool itself. The repo `C:\Users\chris\code\tabmaker` starts empty.

**Expected quality**: on full mixes, the output is a solid **first draft** you correct by ear, not a perfect tab. Strong on lead lines, riffs and clean parts in songs with one guitar. Chord mode covers strummed and dense distorted rhythm parts. Weak on layered guitars and on bends/slides. Every stage writes inspectable intermediates.

---

## Milestones & tasks

### M0: Bootstrap repo, plan & "don't forget" kit · DONE
- [x] M0.1 `git init`, `.gitignore` (`bench/`, `work/`, `feedback/`, audio, model caches, `.venv`)
- [x] M0.2 Copy this plan to `PLAN.md` at the repo root
- [x] M0.3 `uv init` with Python 3.11, src layout, `pytest`; **commit `uv.lock`** so the environment can be rebuilt identically months later
- [x] M0.4 `README.md`: 3-line pitch + two doors, "Use it (guitar player)" → USER-GUIDE and "Work on it (developer)" → DEV-GUIDE + PLAN
- [x] M0.5 `docs/USER-GUIDE.md` skeleton (install, first song, reading the sheet, checking by ear, review, re-run, limits); filled in as features land
- [x] M0.6 `docs/DEV-GUIDE.md`: setup, commands, architecture map (pipeline + modules), how to resume work, Windows/WSL notes
- [x] M0.7 `CHANGELOG.md` (player-language entries per milestone)
- [x] M0.8 `CLAUDE.md`: "start every session by reading `PLAN.md`; follow its maintenance rules; definition of done; commit with task IDs"
- [x] M0.9 `tests/test_plan.py`: the status table matches the milestone headers; a DONE milestone has no `[ ]` tasks; task IDs are unique
- [x] M0.10 Claude memory pointer: project → `PLAN.md` is the source of truth
- [x] M0.11 First commit

**Done when**: a fresh clone + `uv sync` + `uv run pytest` passes, and the README leads to both guides and the plan.

### M1: End-to-end skeleton on a real song · IN PROGRESS
- [x] M1.1 **Install test**: install Demucs, basic-pitch and beat_this together on Windows and run each once on one song (if that fails: WSL + Decision log)
- [x] M1.2 `models.py` (Note, TabNote, Column = notes struck together) + `fretboard.py` (`Tuning` standard, candidate positions)
- [x] M1.3 `separate.py`: Demucs `htdemucs_6s` → `work/<song>/stems/`, cached by file hash
- [x] M1.4 `transcribe.py`: basic-pitch → `notes.mid` + `notes.json`
- [x] M1.5 Naive fingering (lowest fret) + `render/ascii.py` (timestamped lines, no bars)
- [x] M1.6 `cli.py`: `tabmaker song.mp3 [--start --end]`, `rich` progress bars, out-of-range warning
- [x] M1.7 **Per-song memory**: `work/<song>/run.toml` stores the settings; `tabmaker work/<song>` re-runs with them; `tab.txt` header (date, version, milestone, settings)
- [x] M1.8 **Home screen** `tabmaker` (no args): pitch, status from `PLAN.md` (current milestone + next task), songs in `work/` with state, commands, the last CHANGELOG entries. `tabmaker status` = the plan part only
- [x] M1.9 `tabmaker dev doctor` (ffmpeg, torch, CUDA, models) + `tabmaker dev selftest` (end-to-end on a built-in synthetic clip); first-run model-download message
- [x] M1.10 `tabmaker guide` prints/opens USER-GUIDE; every command's `--help` has examples
- [~] M1.11 Docs: `docs/README.md` (tutorial map) ✓, `01-digital-audio.md` ✓, `02-source-separation.md` ✓; still to do: USER-GUIDE "first song", CHANGELOG entry, DEV-GUIDE dependency notes, CLAUDE.md (no stacked branches + learning style)
- [ ] M1.12 CI: install the ML dependencies on both OSes + a `dev selftest` job on Ubuntu with a model cache
- [ ] M1.13 **Guided session** (the user drives, Claude explains): run stage 1 on a real song, listen to `mix.wav` and each stem, read `tab.txt`. This also covers the real-song "Done when" check
- [ ] M1.14 **Labs** `labs/01-digital-audio.ipynb`, `labs/02-source-separation.ipynb` (Jupyter + matplotlib as dev dependencies): plot waveforms/spectrograms, play audio inline, change a parameter and re-run

**Done when**: `uv run tabmaker <real song>.mp3` produces `work/<song>/tab.txt` + stems + MIDI; `tabmaker work/<song>` re-runs from the cache with the saved settings; the home screen shows the song; `dev selftest` passes.

### M2: Evaluation harness · NOT STARTED
- [ ] M2.1 `bench/<song>/` layout + `meta.toml` schema (tuning, GP track, offset, split)
- [ ] M2.2 `reference.py`: GP3-5 (PyGuitarPro), GuitarSet JAMS, plain-text tab
- [ ] M2.3 `align.py`: reference → MIDI → chroma → DTW; manual offset fallback
- [ ] M2.4 `evaluate.py`: transcription F1 (+ octave-tolerant), fingering accuracy (both inputs), separation proxy
- [ ] M2.5 `tabmaker dev eval bench/` → table + `results/<date>.json`; `--report` (bar diff + piano-roll PNG); `--history` (trend)
- [ ] M2.6 GuitarSet baseline; add 2–3 of your songs with references
- [ ] M2.7 Last scores on the home screen; doc `09-evaluation.md`; USER-GUIDE "test it on a song you know"

**Done when**: eval runs on GuitarSet + your songs; `--history` shows the first entry.

### M3: Transcription quality · NOT STARTED
- [ ] M3.1 Cleanup filters: range, minimum duration, confidence, octave/harmonic ghosts
- [ ] M3.2 Onset grouping into chords (<30 ms)
- [ ] M3.3 `?` markers under low-confidence notes
- [ ] M3.4 `--guitar left|right|center` stereo split (saved in `run.toml`)
- [ ] M3.5 Piano-roll dump for inspection
- [ ] M3.6 `play.py` + `tabmaker play --from/--to [--slow] [--source mix|guitar] [--loop]`
- [ ] M3.7 Doc `03-transcription.md`; USER-GUIDE "checking by ear", "two guitars"

**Done when**: benchmark transcription F1 beats M1 (logged), and `play` works.

### M4: Rhythm & bars · NOT STARTED
- [ ] M4.1 `rhythm.py`: beat_this on the full mix (librosa fallback) → tempo map, downbeats
- [ ] M4.2 Quantization: straight vs triplet per beat
- [ ] M4.3 Bars in the output; `play --bars`
- [ ] M4.4 Strum onsets + direction heuristic (for M6)
- [ ] M4.5 Rhythm metrics in eval; unit tests on synthetic onsets
- [ ] M4.6 Doc `04-rhythm.md`; USER-GUIDE "reading bars"

**Done when**: bar lines in `tab.txt` follow the song; the rhythm metrics are in eval.

### M5: Fingering (Viterbi) & tunings · NOT STARTED
- [ ] M5.1 Viterbi with state/transition costs (time-gap scaling), top-K pruning; `fingering_weights.toml`
- [ ] M5.2 Tuning presets `standard|eb|drop-d|custom` + `--tuning` (saved in `run.toml`); suggestions in the range warning
- [ ] M5.3 `play --source tab` (Karplus-Strong synth)
- [ ] M5.4 Unit tests: a C major scale stays in one position; open chords → standard shapes
- [ ] M5.5 Docs `05-fingering.md`, `07-tab-notation.md`; USER-GUIDE "tunings"

**Done when**: benchmark fingering accuracy beats the naive M1 mapping; the tests pass.

### M6: Chord mode · NOT STARTED
- [ ] M6.1 `chords.py`: per-beat CQT chroma, templates {maj, min, 7, maj7, m7, sus2, sus4, 5, N} × 12, Viterbi smoothing → ChordSpans; `--chords-from mix`
- [ ] M6.2 `voicings.py`: shapes per tuning, ranking, Viterbi across the progression
- [ ] M6.3 Strum pattern line under the chord bars
- [ ] M6.4 `segmenter.py` (hysteresis) + `--mode auto|tab|chords` (saved in `run.toml`)
- [ ] M6.5 Renderer: chord bars + chord legend; `play` synthesizes strums
- [ ] M6.6 Eval: `mir_eval.chord`, segmenter agreement, `reference_chords.txt`
- [ ] M6.7 Unit tests: synthetic chroma → label; C in standard includes `x32010`; Eb shifts shapes
- [ ] M6.8 Doc `06-chords.md`; USER-GUIDE "chord sheets"

**Done when**: a strummed song gives a readable chord sheet; the chord metrics are in eval. **This completes the usable tool.**

### M7: Review loop · NOT STARTED
- [ ] M7.1 Diverse alternatives per segment (tab positions ≥ 3 frets apart; chord names, voicings, mode switch)
- [ ] M7.2 `review.txt` writer: uncertain segments only, sorted, ★ ratings, `play` hint, `custom` block, a **how-to header at the top of the file itself**
- [ ] M7.3 Tolerant parser + clear errors
- [ ] M7.4 Apply on re-run: picks as hard constraints; they survive re-runs
- [ ] M7.5 Classify edits: preference vs note/chord correction
- [ ] M7.6 `feedback/choices.jsonl` + automatic perceptron learning (`dev learn` to force)
- [ ] M7.7 Home screen shows the review state per song ("4 segments waiting")
- [ ] M7.8 Golden-file round-trip tests; docs update `05`/`06`, start `10-improving.md`; USER-GUIDE "reviewing"

**Done when**: one song goes from MP3 to a reviewed sheet using only `tabmaker song.mp3` + `tabmaker play`; the weights change after a review.

### M8: Improvement loop · NOT STARTED
- [ ] M8.1 `tune.py`: Optuna over thresholds, grid, chord smoothing, segmenter; train/test split
- [ ] M8.2 Benchmark grown to ~10+ songs (+ GuitarSet)
- [ ] M8.3 Model comparisons (Demucs variants, alternative transcriber, pretrained chord model)
- [ ] M8.4 Finish doc `10-improving.md`

**Done when**: tuned parameters improve the `test` split (logged).

### M9: Guitar Pro 5 export (phase 2) · NOT STARTED
- [ ] M9.1 `render/gp5.py`: notes, rhythm, chord names + diagrams, tuning
- [ ] M9.2 `-o out.gp5` (+ `run.toml`); round-trip test
- [ ] M9.3 Doc `08-guitar-pro-format.md`; USER-GUIDE "open in TuxGuitar"

**Done when**: the exported file opens and plays correctly in TuxGuitar.

### L: Later / ideas · NOT STARTED
- [ ] L.1 `--capo`
- [ ] L.2 Detecting bends/slides/hammer-ons
- [ ] L.3 Fine-tuning transcription on GuitarSet + aligned songs (GPU)
- [ ] L.4 Web UI with alphaTab

---

## Reference design
(Keep this in sync with the code; changes go to the Decision log.)

### Key technical decisions
| Decision | Choice | Why |
|---|---|---|
| Language/env | Python 3.11, `uv` + committed `uv.lock`, src layout | ML tooling is Python; reproducible after long breaks; WSL Ubuntu as the fallback |
| Stem separation | Demucs `htdemucs_6s` | Best open model with a guitar stem |
| Note transcription | Spotify `basic-pitch` | Polyphonic, light, confidence scores; runs on TensorFlow 2.14 (basic-pitch 0.4 requires it on Python 3.11) |
| Beat/tempo | `beat_this` on the full mix, `librosa` fallback | Drums make beats easier to find; avoids `madmom` |
| Fingering | Own Viterbi | No maintained library; its weights hold your learned style |
| Chords | Own chroma + templates + Viterbi | Educational, reuses beats + Viterbi |
| Voicings | Generated from the `Tuning` | Any tuning works automatically |
| Output | Phase 1: `tab.txt`; phase 2: GP5 via PyGuitarPro | Text is easy to debug; GP5 opens in TuxGuitar |
| CLI | `typer` + `rich` | Readable output, built-in help |
| Tuning | List of open-string MIDI pitches, a parameter everywhere | Presets and custom tunings come almost free |
| "Don't forget" kit | home screen, `run.toml`, `tab.txt` header, USER/DEV guides, CHANGELOG, `PLAN.md` + consistency test | Occasional use: the repo and the tool remember, you don't have to |

### Pipeline
```
song.mp3 ─→ separate ─→ guitar stem ─┬─→ transcribe notes ─┐
    └───→ full mix ─→ beats & bars ──┤                     ├─→ segmenter: each bar = tab | chords
                                     └─→ chroma per beat ──┘
  tab bars   ─→ fingering (Viterbi)                          ─┐
  chord bars ─→ chord recognition (Viterbi) ─→ voicing + strum ┴─→ render work/<song>/tab.txt
```

### Repo structure
```
tabmaker/
  README.md  PLAN.md  CHANGELOG.md  CLAUDE.md  pyproject.toml  uv.lock
  src/tabmaker/
    cli.py  home.py (home screen/status)  models.py  separate.py  transcribe.py  rhythm.py
    fretboard.py  fingering.py  chords.py  voicings.py  segmenter.py  review.py  play.py
    reference.py  align.py  evaluate.py  tune.py  selftest.py
    render/ascii.py  render/gp5.py
  tests/ (incl. test_plan.py)
  bench/<song>/audio.mp3, reference.gp5 | reference_chords.txt, meta.toml ; bench/results/<date>.json
  work/<song>/run.toml, stems/, notes.mid, notes.json, segments.json, review.txt, tab.txt
  feedback/choices.jsonl
  docs/USER-GUIDE.md  DEV-GUIDE.md  README.md (tutorial map)
       01-digital-audio  02-source-separation  03-transcription  04-rhythm  05-fingering
       06-chords  07-tab-notation  08-guitar-pro-format  09-evaluation  10-improving
```

### Home screen (illustrative)
```
$ tabmaker
TabMaker: turns a song recording into guitar tab + chord sheets.

Project: M3 Transcription quality (IN PROGRESS) · next task M3.4
Benchmark: note F1 0.62 (prev 0.55, 2026-11-02)

Your songs (work/):
  song_a   sheet ✓  review: 4 segments waiting   2026-11-02 · tuning eb · mode auto
  song_b   sheet ✓  reviewed                     2026-10-20 · standard · mode tab

Commands:
  tabmaker <file.mp3 | work/<song>>   make or update a sheet
  tabmaker play <song> --bars 12-14   listen to a passage (--slow, --loop)
  tabmaker guide                      user guide      ·  tabmaker dev --help  developer tools

New: --guitar left/right/center (M3) …
```

### Tutorial format (each concept doc)
Plain language for a guitarist with no DSP/ML background:
1. The problem
2. Core concepts (diagrams, worked examples)
3. How the tool/algorithm works inside
4. Failure modes
5. Try it yourself
6. Further reading

### User experience
Player commands (developer tools under `tabmaker dev`: eval, tune, learn, doctor, selftest):
- `tabmaker song.mp3 [--mode auto|tab|chords] [--start --end] [--tuning ...] [--guitar left|right|center]`; `tabmaker work/<song>` re-runs with the saved settings and applies the review edits.
- `tabmaker play <song> --bars 12-14 | --from --to [--slow 0.6] [--source mix|guitar|tab] [--loop]`

| Pain point | Fix |
|---|---|
| Forgetting how it works | home screen, USER-GUIDE, `--help` examples, how-to header in `review.txt` |
| Forgetting flags per song | `run.toml` + `tab.txt` header |
| Install on Windows / broken env after a break | `uv.lock`, `dev doctor`, `dev selftest` |
| Slow separation | progress bars, stem cache, `--start/--end` |
| Two guitars in one stem | `--guitar` stereo split |
| Wrong tuning | presets; warning with suggestions |
| Noisy tab on strumming | auto chord mode |
| Checking by ear | `play` (loop, slow, A-B) |
| Finding errors | `?` markers |
| Review overload | only uncertain segments; `tab.txt` usable without review |
| Editing ASCII | tolerant parser |
| Note vs fingering fixes | automatic classification |

### Algorithms
- **Transcription cleanup**: range from the `Tuning`, minimum ~50 ms, confidence threshold, ghost removal, <30 ms grouping.
- **Rhythm**: tempo map; onsets → beat positions; straight vs triplet per beat; downbeats → bars.
- **Fingering**: states = valid string/fret sets (span ≤ 4–5), top-K. State cost = stretch + high fret − open bonus. Transition = hand move + string skip, scaled by the time gap. Viterbi.
- **Chords**: per-beat CQT chroma · cosine vs templates · Viterbi (self-transition + downbeat-change bonus) → ChordSpans.
- **Voicings**: muted or chord tone per string, root lowest, required tones, span ≤ 4; ranked by commonness + stretch; Viterbi over the progression.
- **Strums**: onsets → grid; on-beat down / off-beat up, overridden by string order within the strum.
- **Segmenter**: chords if polyphony > ~2.5, strum-like spread, or low confidence; hysteresis.

### Review & feedback
- The top 3 diverse alternatives per segment (≤ ~2 bars), not whole-song versions; a few KB per song.
- `review.txt`: how-to header, uncertain segments only, ★ ratings, `play` hint, `custom` block.
- Picks = hard Viterbi constraints that survive re-runs. `choices.jsonl` → perceptron weights; corrections → benchmark.

### Evaluation
- **References**: GP3–5 (convert GP6–8 in TuxGuitar), plain-text tab, `reference_chords.txt`, GuitarSet; they must match the exact recording.
- **Alignment**: DTW on chroma, with a manual offset fallback.

| Stage | Metric |
|---|---|
| Separation | transcription F1 on the stem vs the mix |
| Transcription | note F1 ±50 ms, octave-tolerant F1 |
| Rhythm | beat F-measure, grid accuracy |
| Fingering | string/fret accuracy (detected notes / reference pitches) |
| Chords | `mir_eval.chord` majmin/triads |
| Segmenter | mode agreement per bar |

### Improving (in order of effort)
1. Optuna on `train`, held-out `test` (from ~10 songs on)
2. Learned weights
3. Corrections → benchmark
4. Model comparisons
5. Fine-tuning (GPU, personal use)

### Verification (every milestone)
- `uv run pytest` passes (including `test_plan.py`).
- `tabmaker dev selftest` passes.
- From M2 on: `tabmaker dev eval bench/` shows no regression on `test`; scores go into the Progress log.
- End-to-end on a riff/solo song and a strummed song: read `tab.txt` while listening, check with `play`.
- **Returning-user check**: following only README → USER-GUIDE, process a new song without looking at the code or this plan.
- Every "Try it yourself" command in `docs/` runs as written.

---

## Decision log
| Date | Decision |
|---|---|
| 2026-10-16 | Initial plan: Python CLI, full-song input, plain text first then GP5, concept tutorials per stage, evaluation on known songs, review loop, chord mode inside the usable cut line, "don't forget" kit (home screen, per-song settings, guides, changelog, plan consistency test). |
| 2026-10-16 | uv on this Windows machine fails to create the Python minor-version link; workaround `uv sync --python <path to downloaded python.exe>` documented in DEV-GUIDE. Not a reason to switch to WSL. |
| 2026-10-16 | Every milestone is developed on its own branch `m<N>-<slug>` and submitted as a pull request; the user merges. M0 was the initial commit on `main`, made before this rule existed. |
| 2026-10-16 | GitHub Actions CI on PRs and `main`: ruff, locked install, pytest, build, CLI smoke test on Ubuntu + Windows. Once ML dependencies land (M1), CI must cache the models and keep tests that need audio/models short (M1.9 selftest on a tiny clip). |
| 2026-10-16 | Dependencies (M1.1): CPU-only PyTorch from the pytorch-cpu index everywhere (no multi-GB CUDA libraries). basic-pitch 0.4 requires TensorFlow on Python 3.11 (not ONNX as first planned) → constraints `numpy<2` (TF 2.14), `setuptools<81` (resampy imports pkg_resources), `tensorflow-io-gcs-filesystem<0.32` on Windows (no newer Windows wheels). The lock targets Windows + Linux x86_64. Audio is read with soundfile/libsndfile (MP3 included); ffmpeg is optional (M4A only). |
| 2026-10-16 | Learning track (rule 6b): guided sessions, Jupyter labs, and "you code, I coach" for key algorithms, at the user's request: learning by experimenting matters more than code volume. |

## Progress log
| Date | Task(s) | Notes / scores |
|---|---|---|
| 2026-10-16 | M0.1–M0.11 | Repo, uv env (Python 3.11.17), README, USER-GUIDE skeleton, DEV-GUIDE, CHANGELOG, CLAUDE.md, plan consistency test (17 tests pass), memory pointer. No pipeline code yet. |
| 2026-10-16 | M1.1–M1.10, part of M1.11 | Branch `m1-skeleton` (not pushed yet). The pipeline runs end to end. Self-test on the synthetic clip: basic-pitch found 16/16 notes on clean guitar; separation → notes → tab OK; the re-run reuses cached stems. `dev doctor` all OK (ffmpeg absent, optional). 41 unit tests pass. Not yet tried on a real song (M1.13). |
