"""World Cup Oracle — Web UI
Run: python app.py
Then open http://localhost:5000 in your browser.
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from elo import compute_elo_ratings, get_wc_team_ratings
from poisson_model import train_poisson_model
from simulation import match_probabilities, set_goal_model
from worldcup2026 import WC2026_TEAMS, find_team

app = Flask(__name__)

# Load model once at startup
print("Loading Elo ratings...")
all_ratings, match_count, history = compute_elo_ratings(record_history=True)
RATINGS = get_wc_team_ratings(all_ratings)
print(f"Training Poisson model on {match_count:,} matches...")
model = train_poisson_model(history, verbose=False)
set_goal_model(model)
print("Ready.")

TEAM_NAMES = sorted([t.name for t in WC2026_TEAMS])
TEAM_FLAGS = {t.name: t.flag for t in WC2026_TEAMS}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Cup Oracle 2026</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c26;
    --border: #2a2a38;
    --accent: #6c63ff;
    --accent2: #ff6584;
    --green: #00d68f;
    --text: #e8e8f0;
    --muted: #6b6b80;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    padding: 40px 20px;
  }

  .container { max-width: 760px; margin: 0 auto; }

  header { text-align: center; margin-bottom: 48px; }

  .logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 56px;
    letter-spacing: 3px;
    background: linear-gradient(135deg, #6c63ff, #ff6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
  }

  .subtitle {
    color: var(--muted);
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 8px;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 24px;
  }

  .match-inputs {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 16px;
    align-items: center;
  }

  .team-select-wrap { display: flex; flex-direction: column; gap: 8px; }

  label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
  }

  select {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 500;
    padding: 14px 16px;
    width: 100%;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b6b80' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 14px center;
    transition: border-color 0.2s;
  }

  select:focus { outline: none; border-color: var(--accent); }

  .vs {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    color: var(--muted);
    text-align: center;
    padding-top: 20px;
  }

  .predict-btn {
    width: 100%;
    margin-top: 24px;
    padding: 16px;
    background: linear-gradient(135deg, #6c63ff, #8b80ff);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.1s;
  }

  .predict-btn:hover { opacity: 0.9; }
  .predict-btn:active { transform: scale(0.99); }
  .predict-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  #result { display: none; }

  .match-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }

  .team-label {
    text-align: center;
    flex: 1;
  }

  .team-flag { font-size: 36px; line-height: 1; }

  .team-name {
    font-size: 18px;
    font-weight: 600;
    margin-top: 6px;
  }

  .team-elo {
    font-size: 12px;
    color: var(--muted);
    margin-top: 3px;
  }

  .match-vs {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
    color: var(--border);
  }

  .score-display {
    text-align: center;
    margin-bottom: 28px;
  }

  .score-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
  }

  .score {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 64px;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #6c63ff, #ff6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
  }

  .xg-row {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-top: 8px;
    font-size: 13px;
    color: var(--muted);
  }

  .xg-val { color: var(--text); font-weight: 500; }

  .probs-section { margin-top: 28px; }

  .prob-bar-wrap { margin-bottom: 16px; }

  .prob-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }

  .prob-team { font-size: 13px; font-weight: 500; }
  .prob-pct { font-size: 13px; font-weight: 700; }

  .bar-track {
    height: 8px;
    background: var(--surface2);
    border-radius: 99px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s cubic-bezier(.4,0,.2,1);
  }

  .bar-a { background: linear-gradient(90deg, #6c63ff, #8b80ff); }
  .bar-draw { background: linear-gradient(90deg, #f5a623, #f7c948); }
  .bar-b { background: linear-gradient(90deg, #ff6584, #ff8fa3); }

  .spinner {
    display: inline-block;
    width: 18px; height: 18px;
    border: 2px solid rgba(255,255,255,0.2);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    vertical-align: middle;
    margin-right: 8px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .error-msg {
    background: rgba(255, 101, 132, 0.1);
    border: 1px solid rgba(255, 101, 132, 0.3);
    border-radius: 10px;
    padding: 14px 18px;
    color: #ff6584;
    font-size: 14px;
    margin-top: 16px;
    display: none;
  }

  .footer {
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    margin-top: 32px;
  }
</style>
</head>
<body>
<div class="container">

  <header>
    <div class="logo">World Cup Oracle</div>
    <div class="subtitle">2026 FIFA World Cup · Monte Carlo Predictor</div>
  </header>

  <div class="card">
    <div class="match-inputs">
      <div class="team-select-wrap">
        <label>Home Team</label>
        <select id="teamA">
          <option value="">Select team...</option>
          {% for name in teams %}
          <option value="{{ name }}">{{ flags[name] }} {{ name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="vs">VS</div>
      <div class="team-select-wrap">
        <label>Away Team</label>
        <select id="teamB">
          <option value="">Select team...</option>
          {% for name in teams %}
          <option value="{{ name }}">{{ flags[name] }} {{ name }}</option>
          {% endfor %}
        </select>
      </div>
    </div>
    <button class="predict-btn" onclick="predict()">Predict Match</button>
    <div class="error-msg" id="error"></div>
  </div>

  <div class="card" id="result">
    <div class="match-header">
      <div class="team-label">
        <div class="team-flag" id="flagA"></div>
        <div class="team-name" id="nameA"></div>
        <div class="team-elo" id="eloA"></div>
      </div>
      <div class="match-vs">VS</div>
      <div class="team-label">
        <div class="team-flag" id="flagB"></div>
        <div class="team-name" id="nameB"></div>
        <div class="team-elo" id="eloB"></div>
      </div>
    </div>

    <div class="score-display">
      <div class="score-label">Most Likely Score</div>
      <div class="score" id="score"></div>
      <div class="xg-row">
        <span>Expected goals:</span>
        <span class="xg-val" id="xgA"></span>
        <span>–</span>
        <span class="xg-val" id="xgB"></span>
      </div>
    </div>

    <div class="probs-section">
      <div class="prob-bar-wrap">
        <div class="prob-meta">
          <span class="prob-team" id="labelA"></span>
          <span class="prob-pct" id="pctA"></span>
        </div>
        <div class="bar-track"><div class="bar-fill bar-a" id="barA" style="width:0%"></div></div>
      </div>
      <div class="prob-bar-wrap">
        <div class="prob-meta">
          <span class="prob-team">Draw</span>
          <span class="prob-pct" id="pctDraw"></span>
        </div>
        <div class="bar-track"><div class="bar-fill bar-draw" id="barDraw" style="width:0%"></div></div>
      </div>
      <div class="prob-bar-wrap">
        <div class="prob-meta">
          <span class="prob-team" id="labelB"></span>
          <span class="prob-pct" id="pctB"></span>
        </div>
        <div class="bar-track"><div class="bar-fill bar-b" id="barB" style="width:0%"></div></div>
      </div>
    </div>
  </div>

  <div class="footer">Probabilistic model · Not betting advice · Built with Claude</div>
</div>

<script>
async function predict() {
  const a = document.getElementById('teamA').value;
  const b = document.getElementById('teamB').value;
  const err = document.getElementById('error');
  const btn = document.querySelector('.predict-btn');

  err.style.display = 'none';

  if (!a || !b) { err.textContent = 'Please select both teams.'; err.style.display = 'block'; return; }
  if (a === b) { err.textContent = 'Please select two different teams.'; err.style.display = 'block'; return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Simulating 50,000 matches...';
  document.getElementById('result').style.display = 'none';

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team_a: a, team_b: b })
    });
    const d = await res.json();
    if (d.error) { err.textContent = d.error; err.style.display = 'block'; return; }

    document.getElementById('flagA').textContent = d.flag_a;
    document.getElementById('flagB').textContent = d.flag_b;
    document.getElementById('nameA').textContent = d.name_a;
    document.getElementById('nameB').textContent = d.name_b;
    document.getElementById('eloA').textContent = 'Elo ' + d.elo_a;
    document.getElementById('eloB').textContent = 'Elo ' + d.elo_b;
    document.getElementById('score').textContent = d.score;
    document.getElementById('xgA').textContent = d.xg_a;
    document.getElementById('xgB').textContent = d.xg_b;
    document.getElementById('labelA').textContent = d.name_a + ' win';
    document.getElementById('labelB').textContent = d.name_b + ' win';

    const pA = Math.round(d.p_win_a * 100);
    const pD = Math.round(d.p_draw * 100);
    const pB = Math.round(d.p_win_b * 100);

    document.getElementById('pctA').textContent = pA + '%';
    document.getElementById('pctDraw').textContent = pD + '%';
    document.getElementById('pctB').textContent = pB + '%';

    setTimeout(() => {
      document.getElementById('barA').style.width = pA + '%';
      document.getElementById('barDraw').style.width = pD + '%';
      document.getElementById('barB').style.width = pB + '%';
    }, 50);

    document.getElementById('result').style.display = 'block';
  } catch(e) {
    err.textContent = 'Something went wrong. Is the server running?';
    err.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Predict Match';
  }
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, teams=TEAM_NAMES, flags=TEAM_FLAGS)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    a = find_team(data.get('team_a', ''))
    b = find_team(data.get('team_b', ''))

    if not a:
        return jsonify({'error': f"Team not found: {data.get('team_a')}"})
    if not b:
        return jsonify({'error': f"Team not found: {data.get('team_b')}"})
    if a.name == b.name:
        return jsonify({'error': 'Please select two different teams.'})

    elo_a = RATINGS.get(a.name, 1000)
    elo_b = RATINGS.get(b.name, 1000)
    r = match_probabilities(elo_a, elo_b)

    return jsonify({
        'name_a': a.name, 'flag_a': a.flag, 'elo_a': elo_a,
        'name_b': b.name, 'flag_b': b.flag, 'elo_b': elo_b,
        'score': r['most_likely_score'],
        'xg_a': r['xg_a'], 'xg_b': r['xg_b'],
        'p_win_a': r['p_win_a'],
        'p_draw': r['p_draw'],
        'p_win_b': r['p_win_b'],
    })

if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://localhost:5000')
    app.run(debug=False, port=5000)
