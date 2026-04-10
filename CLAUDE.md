# CLAUDE.md — AI Working Rules for wordle-cli

## Project Overview
This is a Python CLI Wordle clone built with Python 3.13. No external dependencies — standard library only.

## Project Structure
```
wordle.py         # Main game loop and entry point
words.py          # WORDS list — the pool of possible answers
valid_words.txt   # Dictionary of accepted guesses for input validation
stats.py          # Win/loss stats tracking (reads/writes stats.json)
stats.json        # Runtime-generated stats file — gitignored, do not commit
```

## Running the Game
```bash
python3 wordle.py
```
The game prompts for hard mode at startup (no CLI flags). Use this command to verify features work before committing.

## Git Workflow
- Never commit directly to `main` — always create a feature branch first.
- Branch naming conventions:
  - `feature/` prefix for new features (e.g. `feature/color-hints`)
  - `fix/` prefix for bug fixes (e.g. `fix/input-validation`)
- Commit messages must be present tense and descriptive (e.g. "Add color hint display" not "Added colors").
- Use the GitHub MCP to create branches, commit, push, and open pull requests.

## Pull Requests
- PR descriptions must explain what changed and why.
- When working on a GitHub issue, reference it in the PR description using `fixes #N`.

## Before Committing
- After implementing a feature or fix, always run the game briefly to verify it works before committing.

## Protected Files
- `valid_words.txt` and `words.py` are core game files — do not remove or replace them.
- `stats.json` is intentionally gitignored — do not add it to version control.
