# TabMaker

Turns a song recording (MP3/WAV) into a guitar sheet: **tab** for riffs and solos, **chords** (names, shapes, strum pattern) for strummed parts.
It's a personal learning project. Every stage (guitar isolation, note detection, rhythm, fingering, chords) comes with a plain-language tutorial explaining how it works.
Expect a good **first draft** to correct by ear, not a perfect tab.

> **Status:** early development, not usable yet. Run `uv run tabmaker` or see [PLAN.md](PLAN.md) for where things stand.

## Pick your door

### 🎸 I want to use it (guitar player)
Read **[docs/USER-GUIDE.md](docs/USER-GUIDE.md)**: install it, make a sheet from a song, read it, check it by ear, review and fix it.

### 🛠 I want to work on it (developer)
1. **[docs/DEV-GUIDE.md](docs/DEV-GUIDE.md)**: setup, commands, architecture, how to resume after a break.
2. **[PLAN.md](PLAN.md)**: the roadmap, with the status of every task. The first unchecked task is the next thing to do.
3. **docs/README.md**: the map of the concept tutorials (how each stage works), arriving in M1.

### 📰 What changed since last time?
**[CHANGELOG.md](CHANGELOG.md)**, written in guitar-player language.
