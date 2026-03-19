"""
styles.py  —  Habitforge design system
Aesthetic: Editorial dark luxury — like a premium fitness journal meets a Bloomberg terminal.
Fonts: Playfair Display (display) + Outfit (body) — refined editorial pairing.
Mobile-first, Streamlit Cloud safe (no global resets, .stApp scoped).
"""

# ── Design tokens ─────────────────────────────────────────────────────────────
BG       = "#080810"
SURFACE  = "#0f0f1a"
CARD     = "#13131f"
BORDER   = "#1c1c2e"
ACCENT   = "#e8c547"      # warm gold — discipline, achievement
ACCENT2  = "#4ade80"      # emerald — completion, success
ACCENT3  = "#38bdf8"      # sky — challenges, community
TEXT     = "#f0f0fa"
MUTED    = "#5a5a7a"
DANGER   = "#f87171"

FONT_URL = "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap"

# ── Avatar colour pool (deterministic from username hash) ─────────────────────
AVATAR_COLORS = [
    "#e8c547","#4ade80","#38bdf8","#f472b6","#a78bfa",
    "#fb923c","#34d399","#60a5fa","#f87171","#c084fc",
]

def avatar_color(seed: str) -> str:
    import hashlib
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[idx]

def avatar_initials(display_name: str) -> str:
    parts = display_name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return display_name[:2].upper()

# ── Full CSS ──────────────────────────────────────────────────────────────────
def get_css() -> str:
    return f"""
<style>
@import url('{FONT_URL}');

/* ── Base ── */
.stApp {{
    background: {BG};
    font-family: 'Outfit', sans-serif;
    color: {TEXT};
}}
section[data-testid="stSidebar"] {{
    background: {SURFACE} !important;
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 99px; }}

/* ── Typography ── */
.hf-display {{
    font-family: 'Playfair Display', serif;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: {TEXT};
    line-height: 1.15;
}}
.hf-label {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {MUTED};
}}

/* ── Buttons ── */
.stButton > button {{
    background: {ACCENT} !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity 0.15s, transform 0.15s !important;
    box-shadow: 0 2px 16px rgba(232,197,71,0.25) !important;
    letter-spacing: 0.02em !important;
}}
.stButton > button:hover {{
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px rgba(232,197,71,0.18) !important;
}}
input[type="password"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {CARD} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid {BORDER} !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 9px !important;
    color: {MUTED} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border: none !important;
    padding: 0.45rem 1rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: {ACCENT} !important;
    color: #0a0a0f !important;
}}

/* ── Progress ── */
.stProgress > div > div > div {{
    background: {ACCENT} !important;
    border-radius: 99px !important;
}}
.stProgress > div > div {{
    background: {BORDER} !important;
    border-radius: 99px !important;
}}

/* ── Metrics ── */
[data-testid="stMetricValue"] {{
    font-family: 'Playfair Display', serif !important;
    color: {ACCENT} !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {MUTED} !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Expander ── */
.stExpander {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
}}
.stExpander summary {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: {TEXT} !important;
}}

/* ── Selectbox dropdown ── */
[data-baseweb="popover"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}

/* ── Radio ── */
.stRadio > div > label {{
    background: transparent !important;
    border-radius: 9px !important;
    padding: 0.5rem 0.85rem !important;
    color: {MUTED} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
    margin-bottom: 2px !important;
    display: block !important;
}}
.stRadio > div > label:hover {{
    background: rgba(232,197,71,0.08) !important;
    color: {TEXT} !important;
}}
[data-testid="stRadio"] [aria-checked="true"] + div {{
    color: {ACCENT} !important;
}}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {ACCENT} !important;
    border-color: {ACCENT} !important;
}}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
    background: {ACCENT} !important;
}}

/* ── Alert/Success ── */
[data-testid="stAlert"] {{
    background: {CARD} !important;
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ════════════════════════════════════════
   COMPONENT CLASSES
   ════════════════════════════════════════ */

/* ── Page header ── */
.hf-page-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.6rem, 4vw, 2.2rem);
    font-weight: 800;
    letter-spacing: -0.025em;
    color: {TEXT};
    line-height: 1.1;
    margin-bottom: 4px;
}}
.hf-page-sub {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.82rem;
    color: {MUTED};
    margin-bottom: 1.5rem;
    font-weight: 400;
}}

/* ── Cards ── */
.hf-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.hf-card:hover {{
    border-color: rgba(232,197,71,0.2);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}}
.hf-card-bar {{
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 3px 0 0 3px;
}}

/* ── Stat tiles ── */
.hf-stat {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.1rem 0.9rem;
    text-align: center;
    transition: border-color 0.2s;
}}
.hf-stat:hover {{ border-color: rgba(232,197,71,0.3); }}
.hf-stat-n {{
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: {ACCENT};
    line-height: 1;
}}
.hf-stat-l {{
    font-size: 0.65rem;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
}}

/* ── Badges / pills ── */
.hf-pill {{
    display: inline-flex; align-items: center; gap: 3px;
    border-radius: 99px; padding: 2px 9px;
    font-size: 0.7rem; font-weight: 700;
    font-family: 'Outfit', sans-serif;
    white-space: nowrap;
}}
.hf-pill-gold  {{ background: rgba(232,197,71,0.12); color: {ACCENT};  border: 1px solid rgba(232,197,71,0.25); }}
.hf-pill-green {{ background: rgba(74,222,128,0.12); color: {ACCENT2}; border: 1px solid rgba(74,222,128,0.25); }}
.hf-pill-sky   {{ background: rgba(56,189,248,0.12); color: {ACCENT3}; border: 1px solid rgba(56,189,248,0.25); }}
.hf-pill-red   {{ background: rgba(248,113,113,0.12); color: {DANGER}; border: 1px solid rgba(248,113,113,0.25); }}

/* ── Avatar ── */
.hf-avatar {{
    width: 36px; height: 36px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'Outfit', sans-serif; font-weight: 700;
    font-size: 0.8rem; color: #0a0a0f; flex-shrink: 0;
}}

/* ── Heatmap ── */
.hf-heatmap {{ display: flex; flex-wrap: wrap; gap: 2px; margin-top: 6px; }}
.hf-hm-cell {{
    width: clamp(10px, 2vw, 13px);
    height: clamp(10px, 2vw, 13px);
    border-radius: 2px;
}}

/* ── Challenge card ── */
.hf-challenge {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.7rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.18s;
}}
.hf-challenge:hover {{
    border-color: rgba(56,189,248,0.3);
    transform: translateY(-2px);
}}
.hf-challenge-enrolled {{
    border-color: rgba(74,222,128,0.35) !important;
    box-shadow: 0 0 18px rgba(74,222,128,0.08);
}}

/* ── Leaderboard row ── */
.hf-lb-row {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: border-color 0.2s;
}}
.hf-lb-row:hover {{ border-color: rgba(232,197,71,0.2); }}
.hf-lb-me {{
    border-color: rgba(232,197,71,0.45) !important;
    background: rgba(232,197,71,0.04) !important;
}}

/* ── Auth form ── */
.hf-auth-wrap {{
    max-width: 420px;
    margin: 2rem auto;
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 2rem 2rem 1.8rem;
}}

/* ── Section title ── */
.hf-section {{
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: {TEXT};
    margin: 1.2rem 0 0.65rem;
    padding-bottom: 6px;
    border-bottom: 1px solid {BORDER};
}}

/* ── Done / undo / delete button overrides ── */
.hf-btn-green button {{
    background: rgba(74,222,128,0.12) !important;
    color: {ACCENT2} !important;
    box-shadow: none !important;
    border: 1px solid rgba(74,222,128,0.25) !important;
}}
.hf-btn-green button:hover {{
    background: rgba(74,222,128,0.22) !important;
    transform: none !important; box-shadow: none !important;
}}
.hf-btn-amber button {{
    background: rgba(232,197,71,0.1) !important;
    color: {ACCENT} !important;
    box-shadow: none !important;
    border: 1px solid rgba(232,197,71,0.2) !important;
}}
.hf-btn-amber button:hover {{ transform: none !important; box-shadow: none !important; }}
.hf-btn-red button {{
    background: rgba(248,113,113,0.1) !important;
    color: {DANGER} !important;
    box-shadow: none !important;
    border: 1px solid rgba(248,113,113,0.2) !important;
}}
.hf-btn-red button:hover {{ transform: none !important; box-shadow: none !important; }}
.hf-btn-sky button {{
    background: rgba(56,189,248,0.1) !important;
    color: {ACCENT3} !important;
    box-shadow: none !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
}}
.hf-btn-sky button:hover {{ transform: none !important; box-shadow: none !important; }}

/* ── Divider ── */
.hf-divider {{
    border: none; border-top: 1px solid {BORDER}; margin: 0.75rem 0;
}}

/* ── Mobile responsiveness ── */
@media (max-width: 768px) {{
    .hf-page-title {{ font-size: 1.45rem !important; }}
    .hf-stat {{ padding: 0.85rem 0.5rem; }}
    .hf-stat-n {{ font-size: 1.4rem; }}
    .hf-card {{ padding: 0.85rem 1rem; }}
    .hf-auth-wrap {{ margin: 1rem; padding: 1.4rem 1.2rem; }}
    section[data-testid="stSidebar"] {{ min-width: 0 !important; }}
}}

/* ── Wordmark ── */
.hf-wordmark {{
    font-family: 'Playfair Display', serif;
    font-weight: 800;
    font-size: 1.5rem;
    letter-spacing: -0.03em;
    color: {ACCENT};
}}
.hf-wordmark-sub {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: {MUTED};
    margin-top: 1px;
}}
</style>
"""

# ── Convenience colour exports ────────────────────────────────────────────────
COLOR_MAP = {
    "#e8c547": "Gold",
    "#4ade80": "Emerald",
    "#38bdf8": "Sky",
    "#f472b6": "Rose",
    "#a78bfa": "Violet",
    "#fb923c": "Tangerine",
    "#34d399": "Mint",
    "#60a5fa": "Blue",
}

QUOTES = [
    "We are what we repeatedly do. Excellence is not an act, but a habit. — Aristotle",
    "Motivation gets you started. Habit keeps you going. — Jim Ryun",
    "You do not rise to the level of your goals. You fall to the level of your systems. — James Clear",
    "Discipline is the bridge between goals and accomplishment. — Jim Rohn",
    "The secret of your future is hidden in your daily routine. — Mike Murdock",
    "Success is the sum of small efforts repeated day in and day out. — Robert Collier",
    "An ounce of practice is worth more than tons of preaching. — Mahatma Gandhi",
    "Your daily choices are your autobiography being written in real time.",
    "Hard choices, easy life. Easy choices, hard life. — Jerzy Gregorek",
    "Every action you take is a vote for the person you wish to become. — James Clear",
    "The quality of your life is determined by the quality of your habits.",
    "Don't count the days. Make the days count. — Muhammad Ali",
    "With self-discipline, almost anything is possible. — Theodore Roosevelt",
    "Fall in love with the process and the results will come.",
    "A year from now you'll wish you had started today.",
    "Be consistent enough that your future self thanks you.",
    "Chains of habit are too light to be felt until they are too heavy to be broken. — Warren Buffett",
    "The man who moves a mountain begins by carrying away small stones. — Confucius",
    "What you do every day matters more than what you do every once in a while.",
    "Do it for who you could be.",
]

BADGE_THRESHOLDS = {
    3:   "🌱 Sprout",
    7:   "🔥 Ignited",
    14:  "⚡ Charged",
    30:  "💎 Diamond",
    60:  "🚀 Elite",
    100: "🏆 Legend",
}

def get_badge(s: int) -> str:
    badge = ""
    for t, n in sorted(BADGE_THRESHOLDS.items(), reverse=True):
        if s >= t: badge = n; break
    return badge
