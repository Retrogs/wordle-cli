#!/usr/bin/env python3

import os
import random
import sys

import stats as st
from words import WORDS

_DICT_PATH = os.path.join(os.path.dirname(__file__), "valid_words.txt")
with open(_DICT_PATH) as _f:
    VALID_WORDS: set[str] = {line.strip() for line in _f if line.strip()}
# Answers are valid guesses too, even if not in the dictionary file
VALID_WORDS |= set(WORDS)

# ANSI escape codes
GREEN_BG  = "\033[42m\033[30m"   # green bg, black text
YELLOW_BG = "\033[43m\033[30m"   # yellow bg, black text
GREY_BG   = "\033[100m\033[97m"  # dark grey bg, white text
EMPTY_BG  = "\033[48;5;236m"     # dark cell for unused rows
RESET     = "\033[0m"
BOLD      = "\033[1m"

EMPTY_ROW = " ".join(f"{EMPTY_BG}   {RESET}" for _ in range(5))

STATUS_PRIORITY = {"green": 2, "yellow": 1, "grey": 0}


def get_feedback(guess, target):
    """Return list of (letter, status) tuples. Handles duplicate letters correctly."""
    result = ["grey"] * 5
    target_pool = list(target)
    guess_chars = list(guess)

    # Pass 1: greens
    for i in range(5):
        if guess_chars[i] == target_pool[i]:
            result[i] = "green"
            target_pool[i] = None
            guess_chars[i] = None

    # Pass 2: yellows
    for i in range(5):
        if guess_chars[i] is None:
            continue
        if guess_chars[i] in target_pool:
            result[i] = "yellow"
            target_pool[target_pool.index(guess_chars[i])] = None

    return list(zip(list(guess), result))


def check_hard_mode(guess, greens, yellows):
    """Return an error string if the guess violates hard mode constraints, else None.

    greens  — dict of {position: letter} that must be reused in the same slot.
    yellows — dict of {letter: set_of_positions_it_was_seen_yellow} that must
              appear somewhere (but not necessarily in those positions).
    """
    for pos, letter in greens.items():
        if guess[pos] != letter:
            ordinal = ["1st", "2nd", "3rd", "4th", "5th"][pos]
            return f"  {ordinal} letter must be {letter}."

    for letter in yellows:
        if letter not in guess:
            return f"  Guess must contain {letter}."

    return None


def tile(letter, status):
    bg = {"green": GREEN_BG, "yellow": YELLOW_BG, "grey": GREY_BG}[status]
    return f"{bg} {letter} {RESET}"


def print_used_letters(used):
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    print()
    for i, row in enumerate(rows):
        indent = "  " * i
        parts = []
        for ch in row:
            if ch in used:
                parts.append(tile(ch, used[ch]))
            else:
                parts.append(f" {ch} ")
        print("  " + indent + " ".join(parts))
    print()


def ask_hard_mode():
    while True:
        try:
            ans = input("  Hard mode? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no", ""):
            return False


def ask_play_again():
    while True:
        try:
            ans = input("  Play again? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no", ""):
            return False


def main():
    print("\033[2J\033[H", end="")
    print(f"\n{BOLD}WORDLE{RESET}  —  6 guesses to find the 5-letter word\n")

    hard_mode = ask_hard_mode()
    mode_label = f"  {BOLD}HARD MODE{RESET}" if hard_mode else ""

    used_words: set[str] = set()

    while True:
        remaining = [w for w in WORDS if w not in used_words]
        if not remaining:
            used_words.clear()
            remaining = WORDS
        target = random.choice(remaining)
        used_words.add(target)

        print("\033[2J\033[H", end="")
        print(f"\n{BOLD}WORDLE{RESET}  —  6 guesses to find the 5-letter word{mode_label}\n")
        for _ in range(6):
            print("  " + EMPTY_ROW)

        used_letters: dict[str, str] = {}
        history: list[str] = []

        # Hard mode constraint state
        greens: dict[int, str] = {}        # position -> confirmed letter
        yellows: dict[str, set[int]] = {}  # letter -> positions where it was yellow

        won = False
        forfeited = False
        for attempt in range(1, 7):
            while True:
                try:
                    raw = input(f"\n  Guess {attempt}/6 (! to forfeit): ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Game aborted.")
                    sys.exit(0)

                if raw == "!":
                    forfeited = True
                    break
                if len(raw) != 5:
                    print("  Must be exactly 5 letters.")
                    continue
                if not raw.isalpha():
                    print("  Letters only, please.")
                    continue
                if raw not in VALID_WORDS:
                    print("  Not in word list.")
                    continue
                if hard_mode:
                    err = check_hard_mode(raw, greens, yellows)
                    if err:
                        print(err)
                        continue
                break

            if forfeited:
                break

            feedback = get_feedback(raw, target)
            row_str = " ".join(tile(ch, status) for ch, status in feedback)
            history.append(row_str)

            # Update hard mode constraints from this guess
            for i, (ch, status) in enumerate(feedback):
                if status == "green":
                    greens[i] = ch
                elif status == "yellow":
                    yellows.setdefault(ch, set()).add(i)

            # Update used-letter map, keeping best status per letter
            for ch, status in feedback:
                if ch not in used_letters or STATUS_PRIORITY[status] > STATUS_PRIORITY[used_letters[ch]]:
                    used_letters[ch] = status

            # Clear screen and reprint everything cleanly
            print("\033[2J\033[H", end="")
            print(f"\n{BOLD}WORDLE{RESET}  —  6 guesses to find the 5-letter word{mode_label}\n")
            for i in range(6):
                print("  " + (history[i] if i < len(history) else EMPTY_ROW))

            print_used_letters(used_letters)

            if raw == target:
                word = "guess" if attempt == 1 else "guesses"
                print(f"\n  {BOLD}You got it in {attempt} {word}!{RESET}\n")
                game_stats = st.load()
                st.record(game_stats, won=True, attempts=attempt)
                st.save(game_stats)
                st.display_result(game_stats, won=True, attempts=attempt)
                won = True
                break

        if not won:
            msg = "You forfeited" if forfeited else "Game over"
            print(f"\n  {BOLD}{msg} — the word was {target}.{RESET}\n")
            game_stats = st.load()
            st.record(game_stats, won=False, attempts=0)
            st.save(game_stats)
            st.display_result(game_stats, won=False, attempts=0)

        if not ask_play_again():
            print("\n  Thanks for playing!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
