"""Save tournament title odds as a LinkedIn-ready PNG."""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from elo import compute_elo_ratings, get_wc_team_ratings
from poisson_model import train_poisson_model
from simulation import run_simulations, set_goal_model
from worldcup2026 import WC2026_TEAMS

print("Loading model (this takes ~30 seconds)...")
all_ratings, match_count, history = compute_elo_ratings(record_history=True)
RATINGS = get_wc_team_ratings(all_ratings)
model = train_poisson_model(history, verbose=False)
set_goal_model(model)

print("Running 10,000 simulations...")
SIM = run_simulations(RATINGS, 10_000)

# Top 16 teams by title odds
rows = sorted(SIM["titles"].items(), key=lambda kv: kv[1], reverse=True)[:16]
TEAM_FLAGS = {t.name: t.flag for t in WC2026_TEAMS}

names  = [r[0] for r in rows]
titles = [100 * r[1] / 10_000 for r in rows]
finals = [100 * SIM["finals"][r[0]] / 10_000 for r in rows]
semis  = [100 * SIM["semi_finals"][r[0]] / 10_000 for r in rows]
flags  = [TEAM_FLAGS.get(n, "") for n in names]

# ── Canvas ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 9), facecolor="#0a0a0f")
ax = fig.add_axes([0.02, 0.08, 0.96, 0.82])
ax.set_facecolor("#0a0a0f")

y = np.arange(len(names))
h = 0.26

# Bars
bars_s = ax.barh(y + h,   semis,  height=h, color="#2a2a4a", label="Semifinal")
bars_f = ax.barh(y,       finals, height=h, color="#534AB7", label="Final")
bars_t = ax.barh(y - h,   titles, height=h, color="#6c63ff", label="Champion")

# Gradient effect on champion bars
for bar, pct in zip(bars_t, titles):
    bar.set_color("#6c63ff")

ax.set_yticks(y)
ax.set_yticklabels([f"{f}  {n}" for f, n in zip(flags, names)],
                   fontsize=11, color="#e8e8f0", fontfamily="monospace")
ax.invert_yaxis()

ax.set_xlabel("Probability (%)", color="#6b6b80", fontsize=10)
ax.tick_params(colors="#6b6b80", labelsize=9)
ax.spines[["top","right","left"]].set_visible(False)
ax.spines["bottom"].set_color("#2a2a38")
ax.xaxis.grid(True, color="#1c1c26", linewidth=0.8)
ax.set_axisbelow(True)

# Value labels
for bar, val in zip(bars_t, titles):
    if val > 0.5:
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}%", va="center", fontsize=8,
                color="#8b80ff", fontweight="bold")

# Legend
legend = ax.legend(loc="lower right", framealpha=0,
                   labelcolor="#e8e8f0", fontsize=9)

# Header
fig.text(0.5, 0.93, "WORLD CUP ORACLE — 2026 FIFA WORLD CUP",
         ha="center", fontsize=13, color="#e8e8f0",
         fontweight="bold", fontfamily="monospace")
fig.text(0.5, 0.905, "Title · Final · Semifinal odds  ·  Monte Carlo 10,000 simulations",
         ha="center", fontsize=9, color="#6b6b80", fontfamily="monospace")

# Footer
fig.text(0.5, 0.02,
         "github.com/Juliagoihman/World-Cup-Oracle-Terminal-Edition  ·  Not betting advice.",
         ha="center", fontsize=7.5, color="#3a3a4a")

# Accent line
fig.add_artist(plt.Line2D([0.02, 0.98], [0.96, 0.96],
               transform=fig.transFigure, color="#6c63ff", linewidth=1.5))

from datetime import datetime
out = f"title_odds_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
plt.savefig(out, dpi=180, bbox_inches="tight",
            facecolor="#0a0a0f", edgecolor="none")
plt.close()
print(f"\nSaved: {out}")
print("Post it on LinkedIn!")
