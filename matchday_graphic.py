"""
World Cup Oracle — LinkedIn Matchday Graphic Generator
Generates a beautiful prediction graphic for knockout stage matches.

Usage:
    python matchday_graphic.py
    python matchday_graphic.py --team_a "Germany" --team_b "France"

Requirements:
    pip install flask pillow matplotlib numpy scikit-learn
"""

import argparse
import os
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from elo import compute_elo_ratings, get_wc_team_ratings
from poisson_model import train_poisson_model
from simulation import match_probabilities, set_goal_model
from worldcup2026 import WC2026_TEAMS, find_team

# ── Load model ──────────────────────────────────────────────────────────────
print("Loading model...")
all_ratings, match_count, history = compute_elo_ratings(record_history=True)
RATINGS = get_wc_team_ratings(all_ratings)
model = train_poisson_model(history, verbose=False)
set_goal_model(model)
TEAM_FLAGS = {t.name: t.flag for t in WC2026_TEAMS}
print("Ready.\n")


def generate_graphic(team_a: str, team_b: str, output_path: str = "prediction.png"):
    a = find_team(team_a)
    b = find_team(team_b)
    if not a or not b:
        print(f"Unknown team: {team_a if not a else team_b}")
        return

    elo_a = RATINGS.get(a.name, 1000)
    elo_b = RATINGS.get(b.name, 1000)
    r = match_probabilities(elo_a, elo_b)

    pA = round(r['p_win_a'] * 100, 1)
    pD = round(r['p_draw'] * 100, 1)
    pB = round(r['p_win_b'] * 100, 1)
    xgA = r['xg_a']
    xgB = r['xg_b']
    score = r['most_likely_score']

    # ── Canvas ───────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(10, 5.6), facecolor='#0a0a0f')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.axis('off')
    ax.set_facecolor('#0a0a0f')

    # ── Background card ──────────────────────────────────────────────────────
    card = FancyBboxPatch((0.3, 0.3), 9.4, 5.0,
                          boxstyle="round,pad=0.15",
                          facecolor='#13131a', edgecolor='#2a2a38', linewidth=1.5)
    ax.add_patch(card)

    # ── Accent gradient strip (top) ──────────────────────────────────────────
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(grad, aspect='auto', extent=[0.3, 9.7, 5.15, 5.3],
              cmap=plt.cm.colors.LinearSegmentedColormap.from_list(
                  'acc', ['#6c63ff', '#ff6584']), zorder=5)

    # ── Header ───────────────────────────────────────────────────────────────
    ax.text(5, 4.82, 'WORLD CUP ORACLE  ·  2026 FIFA WORLD CUP',
            ha='center', va='center', fontsize=7.5, color='#6b6b80',
            fontweight='bold', zorder=6,
            fontfamily='monospace')

    ax.text(5, 4.48, 'KNOCKOUT STAGE PREDICTION',
            ha='center', va='center', fontsize=11, color='#e8e8f0',
            fontweight='bold', zorder=6, fontfamily='monospace')

    # ── Team names & flags ───────────────────────────────────────────────────
    ax.text(2.5, 3.7, TEAM_FLAGS.get(a.name, ''), ha='center', va='center',
            fontsize=38, zorder=6)
    ax.text(7.5, 3.7, TEAM_FLAGS.get(b.name, ''), ha='center', va='center',
            fontsize=38, zorder=6)

    ax.text(2.5, 3.1, a.name.upper(), ha='center', va='center',
            fontsize=13, color='#e8e8f0', fontweight='bold', zorder=6)
    ax.text(7.5, 3.1, b.name.upper(), ha='center', va='center',
            fontsize=13, color='#e8e8f0', fontweight='bold', zorder=6)

    ax.text(2.5, 2.78, f'Elo {elo_a}', ha='center', va='center',
            fontsize=9, color='#6b6b80', zorder=6)
    ax.text(7.5, 2.78, f'Elo {elo_b}', ha='center', va='center',
            fontsize=9, color='#6b6b80', zorder=6)

    # ── VS + Score ───────────────────────────────────────────────────────────
    ax.text(5, 3.62, 'VS', ha='center', va='center',
            fontsize=14, color='#2a2a38', fontweight='bold', zorder=6)
    ax.text(5, 3.15, score, ha='center', va='center',
            fontsize=22, color='#6c63ff', fontweight='bold', zorder=6,
            path_effects=[pe.withStroke(linewidth=3, foreground='#13131a')])
    ax.text(5, 2.82, 'most likely score', ha='center', va='center',
            fontsize=7.5, color='#6b6b80', zorder=6)

    # ── Probability bars ─────────────────────────────────────────────────────
    bar_y = 2.2
    bar_h = 0.28
    bar_x0 = 0.7
    bar_w = 8.6

    # Background track
    track = FancyBboxPatch((bar_x0, bar_y), bar_w, bar_h,
                           boxstyle="round,pad=0.04",
                           facecolor='#1c1c26', edgecolor='none')
    ax.add_patch(track)

    # Segments
    total = pA + pD + pB
    seg_a = bar_w * pA / total
    seg_d = bar_w * pD / total
    seg_b = bar_w * pB / total

    colors_a = ['#6c63ff', '#8b80ff']
    colors_d = ['#f5a623', '#f7c948']
    colors_b = ['#ff6584', '#ff8fa3']

    def draw_segment(x, w, colors, label, pct, side='left'):
        seg = FancyBboxPatch((x, bar_y), w, bar_h,
                             boxstyle="round,pad=0.02",
                             facecolor=colors[0], edgecolor='#0a0a0f', linewidth=1.5)
        ax.add_patch(seg)
        if w > 0.6:
            ax.text(x + w / 2, bar_y + bar_h / 2, f'{pct}%',
                    ha='center', va='center', fontsize=9,
                    color='white', fontweight='bold', zorder=8)

    draw_segment(bar_x0, seg_a, colors_a, a.name, pA)
    draw_segment(bar_x0 + seg_a, seg_d, colors_d, 'Draw', pD)
    draw_segment(bar_x0 + seg_a + seg_d, seg_b, colors_b, b.name, pB)

    # Labels below bar
    ax.text(bar_x0 + seg_a / 2, bar_y - 0.18, f'{a.name} win · {pA}%',
            ha='center', va='center', fontsize=8, color='#8b80ff', fontweight='600', zorder=6)
    ax.text(bar_x0 + seg_a + seg_d / 2, bar_y - 0.18, f'Draw · {pD}%',
            ha='center', va='center', fontsize=8, color='#f5a623', fontweight='600', zorder=6)
    ax.text(bar_x0 + seg_a + seg_d + seg_b / 2, bar_y - 0.18, f'{b.name} win · {pB}%',
            ha='center', va='center', fontsize=8, color='#ff6584', fontweight='600', zorder=6)

    # ── xG row ───────────────────────────────────────────────────────────────
    ax.text(5, 1.52, f'Expected goals:  {a.name} {xgA}  ·  {b.name} {xgB}',
            ha='center', va='center', fontsize=9, color='#6b6b80', zorder=6)

    # ── Footer ───────────────────────────────────────────────────────────────
    ax.text(5, 0.72, 'Monte Carlo simulation · 50,000 match runs · Poisson goal model · Elo ratings from 49k historical matches',
            ha='center', va='center', fontsize=7, color='#3a3a4a', zorder=6)
    ax.text(5, 0.46, 'github.com/Juliagoihman/World-Cup-Oracle-Terminal-Edition  ·  Not betting advice.',
            ha='center', va='center', fontsize=7, color='#3a3a4a', zorder=6)

    # ── Save ─────────────────────────────────────────────────────────────────
    plt.savefig(output_path, dpi=180, bbox_inches='tight',
                facecolor='#0a0a0f', edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def interactive():
    print("World Cup Oracle — LinkedIn Graphic Generator")
    print("=" * 48)
    while True:
        team_a = input("\nTeam A (or 'quit'): ").strip()
        if team_a.lower() in ('quit', 'q', 'exit'):
            break
        team_b = input("Team B: ").strip()
        if not team_a or not team_b:
            continue
        fname = f"prediction_{team_a.replace(' ', '_')}_vs_{team_b.replace(' ', '_')}.png"
        path = generate_graphic(team_a, team_b, fname)
        if path:
            print(f"\nGraphic saved as: {fname}")
            print("Post it on LinkedIn with your prediction!")


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn prediction graphic")
    parser.add_argument('--team_a', type=str, help='First team')
    parser.add_argument('--team_b', type=str, help='Second team')
    parser.add_argument('--output', type=str, default='prediction.png', help='Output filename')
    args = parser.parse_args()

    if args.team_a and args.team_b:
        generate_graphic(args.team_a, args.team_b, args.output)
    else:
        interactive()


if __name__ == '__main__':
    main()
