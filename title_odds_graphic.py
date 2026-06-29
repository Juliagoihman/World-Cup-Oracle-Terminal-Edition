"""World Cup Oracle — Clean White Title Odds Graphic"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from elo import compute_elo_ratings, get_wc_team_ratings
from poisson_model import train_poisson_model
from simulation import run_simulations, set_goal_model
from worldcup2026 import WC2026_TEAMS

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

print("Loading model (takes ~30 seconds)...")
all_ratings, match_count, history = compute_elo_ratings(record_history=True)
RATINGS = get_wc_team_ratings(all_ratings)
model = train_poisson_model(history, verbose=False)
set_goal_model(model)

print("Running 10,000 simulations...")
SIM = run_simulations(RATINGS, 10_000)

rows = sorted(SIM["titles"].items(), key=lambda kv: kv[1], reverse=True)[:16]

names  = [r[0] for r in rows]
titles = [100 * r[1] / 10_000 for r in rows]
finals = [100 * SIM["finals"][r[0]] / 10_000 for r in rows]
semis  = [100 * SIM["semi_finals"][r[0]] / 10_000 for r in rows]

fig, ax = plt.subplots(figsize=(12, 9), facecolor="white")
ax.set_facecolor("white")

y = np.arange(len(names))
h = 0.26

ax.barh(y + h,  semis,  height=h, color="#e0e0e0", label="Semifinal", zorder=3)
ax.barh(y,      finals, height=h, color="#9b9bff", label="Final",     zorder=3)
ax.barh(y - h,  titles, height=h, color="#4a4af0", label="Champion",  zorder=3)

ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=12, color="#111111", fontweight="500")
ax.invert_yaxis()

for bar_y, val in zip(y, titles):
    ax.text(val + 0.2, bar_y - h + h/2, f"{val:.1f}%",
            va="center", fontsize=9, color="#4a4af0", fontweight="bold")

ax.set_xlabel("Probability (%)", color="#666666", fontsize=10, labelpad=10)
ax.tick_params(axis="x", colors="#999999", labelsize=9)
ax.tick_params(axis="y", left=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color("#e0e0e0")
ax.xaxis.grid(True, color="#f0f0f0", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

ax.legend(loc="lower right", framealpha=0,
          labelcolor="#333333", fontsize=9, edgecolor="none")

for i in range(len(names)):
    ax.text(-1.2, y[i], f"{i+1}",
            ha="right", va="center", fontsize=10, color="#999999")

fig.text(0.5, 0.97, "2026 FIFA World Cup — Title Odds",
         ha="center", fontsize=16, color="#111111", fontweight="bold")
fig.text(0.5, 0.945, "Champion · Final · Semifinal probability  ·  Monte Carlo 10,000 simulations",
         ha="center", fontsize=10, color="#888888")

fig.add_artist(plt.Line2D([0.1, 0.9], [0.935, 0.935],
               transform=fig.transFigure, color="#e0e0e0", linewidth=1))

fig.text(0.5, 0.01,
         "github.com/Juliagoihman/World-Cup-Oracle-Terminal-Edition  |  Not betting advice.",
         ha="center", fontsize=8, color="#bbbbbb")

plt.tight_layout(rect=[0.03, 0.03, 1, 0.93])

out = f"title_odds_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close()
print(f"\nSaved: {out}")
print("Ready to post on LinkedIn!")
