#!/usr/bin/env python3

import random
import sys

from words import WORDS

TARGET = random.choice(WORDS)

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


def main():
    print("\033[2J\033[H", end="")
    print(f"\n{BOLD}WORDLE{RESET}  —  6 guesses to find the 5-letter word\n")
    for _ in range(6):
        print("  " + EMPTY_ROW)

    used_letters: dict[str, str] = {}
    history: list[str] = []

    for attempt in range(1, 7):
        while True:
            try:
                raw = input(f"\n  Guess {attempt}/6: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\n  Game aborted.")
                sys.exit(0)

            if len(raw) != 5:
                print("  Must be exactly 5 letters.")
                continue
            if not raw.isalpha():
                print("  Letters only, please.")
                continue
            break

        feedback = get_feedback(raw, TARGET)
        row_str = " ".join(tile(ch, st) for ch, st in feedback)
        history.append(row_str)

        # Update used-letter map, keeping best status per letter
        for ch, st in feedback:
            if ch not in used_letters or STATUS_PRIORITY[st] > STATUS_PRIORITY[used_letters[ch]]:
                used_letters[ch] = st

        # Clear screen and reprint everything cleanly
        print("\033[2J\033[H", end="")
        print(f"\n{BOLD}WORDLE{RESET}  —  6 guesses to find the 5-letter word\n")
        for i in range(6):
            print("  " + (history[i] if i < len(history) else EMPTY_ROW))

        print_used_letters(used_letters)

        if raw == TARGET:
            word = "guess" if attempt == 1 else "guesses"
            print(f"  {BOLD}You got it in {attempt} {word}!{RESET}\n")
            return

    print(f"  {BOLD}Game over — the word was {TARGET}.{RESET}\n")


if __name__ == "__main__":
    main()
