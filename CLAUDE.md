# TabMaker

Personal learning project: a Python CLI that turns a full song recording into guitar tab + chord sheets (Demucs → basic-pitch → beats → Viterbi fingering / chord recognition → plain-text sheet; GP5 export later).

## Start of every session
1. Read `PLAN.md`: the status table, then the current milestone. **It is the single source of truth.**
2. Tell the user where things stand (current milestone, last done task, next task) before proposing work.
3. "Continue the project" means: propose the first unchecked task of the current milestone.

## Rules
- Follow PLAN.md "How this plan is maintained":
  - mark `[~]` while working on a task and `[x]` when it's done;
  - update the status table and the Progress log;
  - log design changes in the Decision log and keep the Reference design in sync.
- **Definition of done**:
  - `uv run pytest` passes (including `tests/test_plan.py`);
  - PLAN.md is updated;
  - for user-visible changes, `docs/USER-GUIDE.md` and `CHANGELOG.md` (player language) are updated;
  - for a concept, its tutorial in `docs/` is updated.
- **One branch + one PR per milestone.**
  - Before the first task of a milestone, `git switch main && git pull`, then `git switch -c m<N>-<slug>`. Never commit milestone work to `main`.
  - Commit messages start with the task ID: `M3.2: ghost-note filter`. Batch pushes: push only once a set of related changes is complete.
  - When "Done when" passes, open a PR `M<N>: <title>` listing the tasks done, how they were verified, and what the user should check by ear. Then hand the merge to the user. Don't merge it yourself unless asked.
  - Fixes outside a milestone get their own short branch + PR.
- The concept tutorials (`docs/NN-*.md`) explain DSP/music/ML for a guitarist, not Python. Follow the 6-part format in PLAN.md.
- Never commit audio, `work/`, `bench/` or `feedback/` (copyrighted or personal data).

## Environment
- Windows + Git Bash; WSL Ubuntu is the fallback for ML dependencies that won't install natively.
- Python 3.11 via uv (`requires-python >=3.11,<3.12`). If `uv sync` fails with "Missing expected target directory for Python minor version link", see `docs/DEV-GUIDE.md` → Known Windows quirk.
- Prefix long-running shell commands with `timeout`: a compound command once hung in this environment.
