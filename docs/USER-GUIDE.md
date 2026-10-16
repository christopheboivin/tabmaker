# TabMaker user guide (for guitar players)

> **Status:** nothing here works yet. Each section says which milestone (see [PLAN.md](../PLAN.md)) makes it real, and is filled in when that milestone lands.
> Forgot everything? Run `uv run tabmaker` (no arguments). The home screen shows the status, your songs and the commands *(M1.8)*.

## What TabMaker does and doesn't do
- **Does:** isolates the guitar from a full song, detects the notes, places them in bars, picks comfortable string/fret positions, and writes chord names + shapes + strum pattern for strummed parts.
- **Doesn't (yet):** bends, slides, hammer-ons, vibrato; reliably separating two guitars playing at once.
- **Works best on:** lead lines, riffs, clean or acoustic parts, songs with one guitar.
- **Works worst on:** dense distorted rhythm parts (chord mode helps), layered or double-tracked guitars.

The result is a **first draft**. You check it by ear and fix it, and the tool learns from your fixes.

## 1. Install *(M0/M1)*
You need [uv](https://docs.astral.sh/uv/) and `git`. Then, in the project folder:
```bash
uv sync
```
```bash
uv run tabmaker dev doctor
```
`dev doctor` *(M1.9)* checks that everything is installed (ffmpeg, models, GPU). The first real run downloads the AI models (a few hundred MB, once).

## 2. Your first song *(M1)*
```bash
uv run tabmaker "path/to/song.mp3"
```
This creates `work/<song>/` with:
- `tab.txt`: the sheet;
- `stems/`: the separated instruments, so you can listen to `guitar.wav` to hear what the tool heard;
- `run.toml`: the settings used, so a later re-run doesn't need you to remember them.

Process only part of a song (faster):
```bash
uv run tabmaker "song.mp3" --start 1:05 --end 1:40
```
Re-run later with the same settings:
```bash
uv run tabmaker work/<song>
```

## 3. Reading the sheet *(M1, M4, M6)*
*To be written:* the header (how and when it was made), timestamps, bars, `?` markers on doubtful notes, the chord legend and the strum line.

## 4. Checking by ear *(M3)*
*To be written:* `tabmaker play` (loop a passage, slow it down, switch between the full mix, the guitar alone and a synthesized version of the tab).

## 5. Tunings *(M5)*
*To be written:* `--tuning standard|eb|drop-d|E2,A2,...`, and what the "notes below low E" warning means.

## 6. Two guitars in the song *(M3)*
*To be written:* `--guitar left|right|center`.

## 7. Chord sheets *(M6)*
*To be written:* `--mode auto|tab|chords`.

## 8. Reviewing and fixing *(M7)*
*To be written:* `review.txt` (pick A/B/C or write your own), then re-run. Your fixes teach the tool your style.

## 9. Testing it on a song you already know *(M2)*
*To be written:* put a song and its correct tab in `bench/`, then run `tabmaker dev eval`.

## 10. Guitar Pro / TuxGuitar *(M9)*
*To be written:* `-o song.gp5`.

## Troubleshooting
*To be written as problems show up.* First step, always: `uv run tabmaker dev doctor`.
