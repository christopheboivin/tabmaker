# Session journal

Where we left off, in plain words. **The newest session is at the top.** Read the top entry first when you come back.
(For the detailed task list see [PLAN.md](PLAN.md); for what changed for you as a player, see [CHANGELOG.md](CHANGELOG.md).)

---

## 2026-10-16 · Session 2: first real song (M1.13 guided session)

### What we did
- Ran the pipeline on *Come As You Are* (0:00–1:00) and listened to `mix.wav` and the stems: guitar, bass and other.
- Read the first lines of `tab.txt` and compared them with how you play the riff.
- Checked M1's "Done when" on a real song: the sheet, stems and MIDI were produced; the re-run reused the stems (7 s); the home screen lists the song; `dev selftest` passed. **M1.13 is done.**

### What we learned
1. **Separation can drop the guitar for a few seconds.** From 0:18 to 0:30 the guitar stem is almost silent, but the guitar didn't stop: Demucs put it in `other.wav`. It decides moment by moment, and the watery chorus effect stopped sounding like "guitar" to it once the vocals came in. (Idea L.5 in the plan.)
2. **The bass doubles the riff**, an octave lower. Same notes at the same time make separation harder.
3. **The song is in D standard** (every string a whole step down), not drop D. The notes prove it: the open low string sounds D2, and the open A string sounds G2, 5 semitones higher. In drop D it would be A2. Our tool only knows standard tuning, so the real low notes were thrown out as "below E2" (M5.2 adds tunings).
4. **Octave errors**: basic-pitch often heard the riff one octave too high (D3/E3 instead of D2/E2). Those ghost notes are why the tab shows the riff on the D string. (M3.1 filters them.)
5. **Hugging Face**: Demucs downloads its model from the Hugging Face Hub and checks it for updates on every run. That causes the "unauthenticated requests" warning. It's harmless and needs no token, but it means the tool isn't fully offline yet (new task M1.15).
6. To find out which stage caused a mistake, start with the parts where the guitar plays alone (the intro): separation can't go wrong there.

### Where things stand
- Branch `m1-skeleton` (draft PR). M1.1–M1.10 and M1.13 are done.
- Left in M1: the labs (M1.14), docs (M1.11), CI for the ML libraries (M1.12) and the offline model load (M1.15).
- If you haven't yet: read [docs/02-source-separation.md](docs/02-source-separation.md). It explains today's "masks" idea, and its "Failure modes" table now includes what we heard.

### Next time: start here
```bash
git switch m1-skeleton
```
```bash
uv run tabmaker
```
Then tell Claude: **"continue the project: labs M1.14"**. You'll open a notebook, plot the spectrogram of `mix.wav` next to `guitar.wav` and `other.wav`, and see the 0:18–0:30 hole for yourself.

---

## 2026-10-16 · Session 1: plan, setup, first working pipeline

### What we did
1. **Designed the project together** (it's all in [PLAN.md](PLAN.md)):
   - The input is a real song recording.
   - The output is a plain-text sheet: tab for riffs and solos, chord names and shapes for strummed parts. Guitar Pro export comes later (M9).
   - Each stage gets a tutorial explaining how it works.
   - You can test the tool on songs whose correct tab you know, and it learns from your corrections.
2. **M0 (done, merged)**: repo, Python 3.11 environment, README, user and developer guides, changelog, and a test that keeps PLAN.md consistent.
3. **Rules we agreed on**:
   - One branch + one pull request per milestone; you merge (PR #1).
   - GitHub CI checks every PR on Windows and Linux; merge only when green (PR #2).
   - New branches always start from `main`. I once stacked a branch on another PR's branch, and that caused the merge conflict you asked me to fix.
4. **M1 (in progress, branch `m1-skeleton`)**: the first full pipeline. It works on a built-in synthetic test clip:
   `song → Demucs isolates the guitar → basic-pitch detects notes → lowest-fret placement → tab.txt`
   - `tabmaker` with no arguments shows a home screen: status, your songs, commands.
   - `tabmaker dev doctor` checks the installation; `tabmaker dev selftest` runs the whole chain on the test clip.
   - Settings are remembered per song (`work/<song>/run.toml`).
5. **Two tutorials written**: [docs/01-digital-audio.md](docs/01-digital-audio.md) (samples, pitch, MIDI numbers, harmonics, spectrograms) and [docs/02-source-separation.md](docs/02-source-separation.md) (how Demucs pulls the guitar out).

### What we learned along the way
- **The ML libraries are picky about versions.** basic-pitch needs TensorFlow on Python 3.11, which needs numpy 1.x and an older setuptools. These pins are in `pyproject.toml`, with the reasons written next to them.
- **Note detection works**: on a clean synthetic guitar it found all 16 notes of the test riff.
- **Harmonics show up as extra high notes.** In the test sheet, the 21/22 frets on the high e string are harmonics detected as notes; M3 will filter them.
- **Separation is the slow step on a CPU** (about as long as the audio). That's why stems are cached and `--start/--end` exist.

### How you want to work from now on
You want to **learn by experimenting**, not watch me generate lots of code. So for every stage:
1. **Guided session**: you run it on a real song, listen to and look at the result, and I explain what happened.
2. **Jupyter lab**: a notebook per stage, where you plot, listen and change a parameter.
3. **You code, I coach**: for the key algorithms (rhythm quantization, fingering, chords), you write the core with hints and tests.

### Where things stand
- `main` = M0 + the branch/PR rule + CI.
- Branch `m1-skeleton` = the M1 code. It's pushed to GitHub as a **draft PR**: it's not finished, but it's saved online.
- **Not done yet in M1**:
  - the guided session on a real song (M1.13);
  - the two labs (M1.14);
  - CI for the heavy ML libraries (M1.12);
  - a few doc updates (M1.11).

### Next time: start here
1. Open the project folder and run:
   ```bash
   git switch m1-skeleton
   ```
   ```bash
   uv run tabmaker
   ```
   The home screen shows the status and the next task.
2. Pick a song you own with a clear guitar part, and note a 30-second section you know well.
3. Tell Claude: **"continue the project: guided session M1.13"**. You'll run:
   ```bash
   uv run tabmaker "path/to/song.mp3" --start 0:30 --end 1:00
   ```
   Then you'll listen to `work/<song>/stems/guitar.wav` and the other stems, read `work/<song>/tab.txt`, and talk about what worked and what didn't.
4. Then the labs (M1.14), then merge the M1 PR and start M2.

Optional reading before then: tutorials 01 and 02 (about 15 minutes each).

### Good to know
- The first real run downloads the AI models once. After that everything runs offline.
- If `uv sync` complains about a "Python minor version link", see [docs/DEV-GUIDE.md](docs/DEV-GUIDE.md) → "Known Windows quirk".
- Your songs and results in `work/` never go to GitHub (they're in `.gitignore`).
