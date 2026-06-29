"""
World Cup Oracle — Auto Scheduler
Watches the match schedule and saves title-odds snapshots
30 min before and 30 min after every game.
Also tracks how odds evolve over time and saves a trend chart.

Run once and leave it running:
    python scheduler.py

Requirements:
    pip install requests matplotlib numpy scikit-learn
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, timedelta, timezone

import requests
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from elo import compute_elo_ratings, get_wc_team_ratings
from poisson_model import train_poisson_model
from simulation import run_simulations, set_goal_model
from worldcup2026 import WC2026_TEAMS

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR   = r"C:\Users\julia\OneDrive\Dokumente\WorldCupOracle"
HISTORY_FILE = os.path.join(OUTPUT_DIR, "odds_history.json")
CHECK_EVERY  = 60   # seconds between schedule checks
TOP_N        = 10   # teams to track in trend chart

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Fetch live schedule from public API ───────────────────────────────────────
SCHEDULE_URL = "https://raw.githubusercontent.com/openfootball/world-cup.json/master/2026/worldcup.json"

def fetch_schedule():
    """Return list of {home, away, kickoff (UTC datetime)} dicts."""
    try:
        r = requests.get(SCHEDULE_URL, timeout=10)
        data = r.json()
        matches = []
        for rnd in data.get("rounds", []):
            for m in rnd.get("matches", []):
                dt_str = m.get("date", "") + "T" + m.get("time", "00:00") + ":00Z"
                try:
                    ko = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                    matches.append({
                        "home": m["team1"].get("name", "?"),
                        "away": m["team2"].get("name", "?"),
                        "kickoff": ko,
                    })
                except Exception:
                    pass
        return matches
    except Exception as e:
        print(f"[scheduler] Could not fetch schedule: {e}")
        return []


# ── Model loader (cached) ─────────────────────────────────────────────────────
_model_cache = {}

def load_model(force=False):
    global _model_cache
    if _model_cache and not force:
        return _model_cache
    print("[model] Loading Elo + Poisson model...")
    all_ratings, _, history = compute_elo_ratings(record_history=True)
    ratings = get_wc_team_ratings(all_ratings)
    model = train_poisson_model(history, verbose=False)
    set_goal_model(model)
    _model_cache = {"ratings": ratings, "model": model}
    print("[model] Ready.")
    return _model_cache


# ── Snapshot ──────────────────────────────────────────────────────────────────
def take_snapshot(label: str, match_desc: str):
    """Compute odds, save PNG and append to history JSON."""
    print(f"\n[snapshot] {label} — {match_desc}")

    # Force fresh Elo (delete cache so live results are included)
    cache = os.path.join(os.path.dirname(__file__), ".cache_results.csv")
    if os.path.exists(cache):
        os.remove(cache)

    m = load_model(force=True)
    ratings = m["ratings"]

    print("[snapshot] Running 10,000 simulations...")
    sim = run_simulations(ratings, 10_000)

    rows  = sorted(sim["titles"].items(), key=lambda kv: kv[1], reverse=True)[:16]
    names = [r[0] for r in rows]
    odds  = {r[0]: round(100 * r[1] / 10_000, 2) for r in rows}

    # ── Save PNG ──────────────────────────────────────────────────────────────
    titles_list = [100 * sim["titles"][n] / 10_000 for n in names]
    finals_list = [100 * sim["finals"][n]  / 10_000 for n in names]
    semis_list  = [100 * sim["semi_finals"][n] / 10_000 for n in names]

    fig, ax = plt.subplots(figsize=(12, 9), facecolor="white")
    ax.set_facecolor("white")

    y = np.arange(len(names))
    h = 0.26

    ax.barh(y + h, semis_list,  height=h, color="#e0e0e0", label="Semifinal", zorder=3)
    ax.barh(y,     finals_list, height=h, color="#9b9bff", label="Final",     zorder=3)
    ax.barh(y - h, titles_list, height=h, color="#4a4af0", label="Champion",  zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=12, color="#111111")
    ax.invert_yaxis()

    for bar_y, val in zip(y, titles_list):
        ax.text(val + 0.2, bar_y - h + h/2, f"{val:.1f}%",
                va="center", fontsize=9, color="#4a4af0", fontweight="bold")

    ax.set_xlabel("Probability (%)", color="#666666", fontsize=10, labelpad=10)
    ax.tick_params(axis="x", colors="#999999", labelsize=9)
    ax.tick_params(axis="y", left=False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#e0e0e0")
    ax.xaxis.grid(True, color="#f0f0f0", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", framealpha=0, labelcolor="#333333",
              fontsize=9, edgecolor="none")

    for i in range(len(names)):
        ax.text(-1.2, y[i], f"{i+1}", ha="right", va="center",
                fontsize=10, color="#999999")

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    safe_label = label.replace(" ", "_").replace(":", "")
    title_str = f"2026 FIFA World Cup — Title Odds\n{label}: {match_desc}"
    fig.text(0.5, 0.97, "2026 FIFA World Cup — Title Odds",
             ha="center", fontsize=16, color="#111111", fontweight="bold")
    fig.text(0.5, 0.945, f"{label}  ·  {match_desc}  ·  {datetime.now().strftime('%d %b %Y %H:%M')}",
             ha="center", fontsize=10, color="#888888")
    fig.add_artist(plt.Line2D([0.1, 0.9], [0.935, 0.935],
                   transform=fig.transFigure, color="#e0e0e0", linewidth=1))
    fig.text(0.5, 0.01,
             "github.com/Juliagoihman/World-Cup-Oracle-Terminal-Edition  |  Not betting advice.",
             ha="center", fontsize=8, color="#bbbbbb")
    plt.tight_layout(rect=[0.03, 0.03, 1, 0.93])

    png_path = os.path.join(OUTPUT_DIR, f"title_odds_{safe_label}_{ts}.png")
    plt.savefig(png_path, dpi=180, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"[snapshot] Saved: {png_path}")

    # ── Append to history JSON ────────────────────────────────────────────────
    entry = {
        "timestamp": datetime.now().isoformat(),
        "label": label,
        "match": match_desc,
        "odds": odds,
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    save_trend_chart(history)


# ── Trend chart ───────────────────────────────────────────────────────────────
def save_trend_chart(history: list):
    """Plot how each top team's title odds changed over time."""
    if len(history) < 2:
        return

    # Find top N teams by latest odds
    latest = history[-1]["odds"]
    top_teams = sorted(latest, key=latest.get, reverse=True)[:TOP_N]

    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in history]
    labels_x   = [f"{e['label']}\n{e['match'][:20]}" for e in history]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor="white")
    ax.set_facecolor("white")

    colors = plt.cm.tab10.colors
    for i, team in enumerate(top_teams):
        vals = [e["odds"].get(team, 0) for e in history]
        ax.plot(range(len(history)), vals,
                marker="o", linewidth=2, markersize=5,
                color=colors[i % 10], label=team)
        # Label at end
        ax.text(len(history) - 0.8, vals[-1], f" {team}",
                va="center", fontsize=8, color=colors[i % 10])

    ax.set_xticks(range(len(history)))
    ax.set_xticklabels(labels_x, fontsize=7, rotation=30, ha="right", color="#666666")
    ax.set_ylabel("Champion probability (%)", color="#666666", fontsize=10)
    ax.tick_params(axis="y", colors="#999999", labelsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#e0e0e0")
    ax.spines["bottom"].set_color("#e0e0e0")
    ax.yaxis.grid(True, color="#f0f0f0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", framealpha=0, fontsize=8,
              labelcolor="#333333", edgecolor="none")

    fig.text(0.5, 0.97, "2026 FIFA World Cup — Title Odds Over Time",
             ha="center", fontsize=15, color="#111111", fontweight="bold")
    fig.text(0.5, 0.945, f"Top {TOP_N} teams  ·  Updated {datetime.now().strftime('%d %b %Y %H:%M')}",
             ha="center", fontsize=10, color="#888888")
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.935, 0.935],
                   transform=fig.transFigure, color="#e0e0e0", linewidth=1))
    fig.text(0.5, 0.01,
             "github.com/Juliagoihman/World-Cup-Oracle-Terminal-Edition  |  Not betting advice.",
             ha="center", fontsize=8, color="#bbbbbb")

    plt.tight_layout(rect=[0, 0.03, 0.88, 0.93])

    trend_path = os.path.join(OUTPUT_DIR, "title_odds_TREND.png")
    plt.savefig(trend_path, dpi=180, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"[trend] Saved: {trend_path}")


# ── Scheduler ─────────────────────────────────────────────────────────────────
def run_scheduler():
    print(f"[scheduler] Starting — checking every {CHECK_EVERY}s")
    print(f"[scheduler] Saving to: {OUTPUT_DIR}")

    scheduled = set()  # track already-scheduled snapshots

    while True:
        now = datetime.now(timezone.utc)
        matches = fetch_schedule()

        for m in matches:
            ko = m["kickoff"]
            desc = f"{m['home']} vs {m['away']}"

            before_key = f"BEFORE_{desc}_{ko.date()}"
            after_key  = f"AFTER_{desc}_{ko.date()}"

            # 30 min before kickoff
            if before_key not in scheduled:
                delta = (ko - timedelta(minutes=30)) - now
                secs  = delta.total_seconds()
                if -60 < secs < 60:  # within 1 min of trigger time
                    scheduled.add(before_key)
                    threading.Thread(
                        target=take_snapshot,
                        args=("BEFORE kickoff", desc),
                        daemon=True
                    ).start()

            # 30 min after kickoff (approx end of 90min = 60 min after trigger)
            if after_key not in scheduled:
                delta = (ko + timedelta(minutes=120)) - now
                secs  = delta.total_seconds()
                if -60 < secs < 60:
                    scheduled.add(after_key)
                    threading.Thread(
                        target=take_snapshot,
                        args=("AFTER match", desc),
                        daemon=True
                    ).start()

        next_check = datetime.now().strftime("%H:%M:%S")
        upcoming = [
            m for m in matches
            if abs(((m["kickoff"] - timedelta(minutes=30)) - now).total_seconds()) < 3600
            or abs(((m["kickoff"] + timedelta(minutes=120)) - now).total_seconds()) < 3600
        ]
        if upcoming:
            print(f"[{next_check}] Upcoming triggers: {[m['home']+' vs '+m['away'] for m in upcoming]}")

        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    print("=" * 55)
    print("  World Cup Oracle — Auto Scheduler")
    print(f"  Output: {OUTPUT_DIR}")
    print("  Saves snapshots 30min before + after each game")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n[scheduler] Stopped.")
