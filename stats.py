import json
import os

STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")

DEFAULTS = {
    "games_played": 0,
    "wins": 0,
    "current_streak": 0,
    "best_streak": 0,
    "guess_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0},
}


def load() -> dict:
    if not os.path.exists(STATS_FILE):
        return {**DEFAULTS, "guess_distribution": dict(DEFAULTS["guess_distribution"])}
    with open(STATS_FILE) as f:
        data = json.load(f)
    # Fill in any keys missing from older saves
    for key, val in DEFAULTS.items():
        data.setdefault(key, val)
    return data


def save(stats: dict) -> None:
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def record(stats: dict, won: bool, attempts: int) -> None:
    stats["games_played"] += 1
    if won:
        stats["wins"] += 1
        stats["current_streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        stats["guess_distribution"][str(attempts)] += 1
    else:
        stats["current_streak"] = 0


def display_result(stats: dict, won: bool, attempts: int) -> None:
    """Show the stats summary, highlighting the current game's row."""
    games = stats["games_played"]
    wins  = stats["wins"]
    pct   = round(wins / games * 100) if games else 0

    BAR   = "\033[42m\033[30m"
    RESET = "\033[0m"

    print("  ┌─────────────────────────┐")
    print("  │        STATISTICS       │")
    print("  ├──────────┬──────────────┤")
    print(f"  │  Played  │  {games:<12}│")
    print(f"  │  Win %   │  {pct:<12}│")
    print(f"  │  Streak  │  {stats['current_streak']:<12}│")
    print(f"  │  Best    │  {stats['best_streak']:<12}│")
    print("  ├──────────┴──────────────┤")
    print("  │    GUESS DISTRIBUTION   │")
    print("  │                         │")

    dist = stats["guess_distribution"]
    peak = max((dist[str(i)] for i in range(1, 7)), default=1) or 1

    for i in range(1, 7):
        count   = dist[str(i)]
        bar_len = max(1, round(count / peak * 14)) if count else 0
        bar     = f"{BAR}{' ' * bar_len}{RESET}" if bar_len else ""
        marker  = " ◄" if won and i == attempts else "  "
        print(f"  │  {i}  {bar}{' ' * (14 - bar_len)} {count:<3}{marker}│")

    print("  └─────────────────────────┘")
    print()
