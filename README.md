# World-Cup-Oracle-Terminal-Edition

> Built in one weekend to avoid paying a crate of beer at Kicktipp. It worked (mostly).

A dependency-free Python CLI that predicts the 2026 FIFA World Cup. It computes Elo ratings from ~49,000 historical international matches, feeds them into a Poisson scoring model, and runs a Monte Carlo simulation of the full 48-team tournament (10,000 runs by default).

My dad is a sports journalist: I grew up with match analysis at the dinner table. When the 2026 group stage started going badly for my Kicktipp predictions, I decided gut feeling wasn't good enough anymore.

---

## What it does

- Computes **Elo ratings** for every national team from ~49,000 historical results
- Runs **10,000 Monte Carlo simulations** of the full tournament
- Outputs **title odds, final odds, semifinal odds** for all 48 teams
- Interactive **head-to-head prompt**: type any two teams, get win/draw/loss probabilities, expected goals, and the most likely scoreline
- **Live dataset** — already includes played 2026 World Cup matches; ratings update as the tournament progresses

---

## Requirements

Python 3.10+ — no third-party packages. Standard library only.

---

## Run

```bash
python oracle.py
```

```bash
python oracle.py --sims 2000   # fewer simulations = faster, slightly noisier
```

On first run it downloads the historical results dataset and caches it locally as `.cache_results.csv`. Later runs are offline and instant. Delete the file to refresh.

---

## Interactive prompt

```
> Brazil vs France      # head-to-head prediction
> titles                # reprint full title-odds table
> teams                 # list all 48 teams + groups
> quit
```

Team names are matched loosely — `Brazil`, `BRA`, or `bra` all work.

---

## The 48 teams & groups

Groups follow the official FIFA final draw, held 5 December 2025 in Washington D.C.

| Group | Teams |
|-------|-------|
| A | Mexico · South Africa · South Korea · Czech Republic |
| B | Canada · Bosnia & Herzegovina · Qatar · Switzerland |
| C | Brazil · Morocco · Haiti · Scotland |
| D | USA · Paraguay · Australia · Turkey |
| E | Germany · Curaçao · Ivory Coast · Ecuador |
| F | Netherlands · Japan · Sweden · Tunisia |
| G | Belgium · Egypt · Iran · New Zealand |
| H | Spain · Cape Verde · Saudi Arabia · Uruguay |
| I | France · Senegal · Iraq · Norway |
| J | Argentina · Algeria · Austria · Jordan |
| K | Portugal · DR Congo · Uzbekistan · Colombia |
| L | England · Croatia · Ghana · Panama |

---

## How it works

| File | Responsibility |
|------|----------------|
| `elo.py` | Downloads results, replays them chronologically, computes Elo ratings |
| `simulation.py` | Poisson expected-goals model + Monte Carlo group stage and knockout bracket |
| `worldcup2026.py` | 48 qualified teams, group assignments, dataset name mapping |
| `oracle.py` | CLI — wires everything together, renders tables and prompt |

### The model

**Elo:** every historical match nudges each team's rating toward its result, weighted by match importance (World Cup > continental > qualifier > friendly), goal margin, and home advantage. Teams start at 1000.

**Expected goals:** the Elo gap between two teams is converted into a share of ~2.5 total expected goals.

**Match outcome:** each side's goals are drawn independently from a Poisson distribution.

**Tournament structure:** 12 groups of 4 play round-robin. The top two from each group plus the eight best third-place teams advance to a 32-team knockout bracket. The bracket follows the real FIFA format — group winners are protected from each other in the Round of 32, and a group's winner and runner-up sit in opposite halves so they can only meet again in the final. Knockout ties go to a lightly Elo-weighted penalty shootout. Repeat 10,000 times.

The trickiest part: replicating FIFA's third-place qualification lookup table, which determines which third-place teams advance based on which specific groups they came from. Turns out that's not a few lines of code.

---

## Built with

Python 3.10+ · Standard library only · Claude (pair programming)

---

## What's next

Formula 1 predictor, or a Euro 2028 simulator. F1 is a messier problem — constructor performance, driver form, circuit characteristics, weather — which makes it more interesting.

---

> Predictions are a probabilistic model for entertainment. Not betting advice. My Kicktipp ranking going up is purely coincidental.
