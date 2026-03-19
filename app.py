import streamlit as st
import json
import os
import uuid
import hashlib
from datetime import date, timedelta
from config import (
    HABITS_FILE, LOGS_FILE, QUOTES, BADGE_THRESHOLDS,
    PAGE_TITLE, ACCENT, BG_DARK, CARD_BG, TEXT_PRIMARY, TEXT_MUTED
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, page_icon="🔥", layout="wide")

# ── CSS  (NO global resets, NO display:none on Streamlit internals) ───────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

.stApp {{
    background: {BG_DARK};
    background-image: radial-gradient(ellipse at 20% 10%, #1a1a2e 0%, {BG_DARK} 60%);
}}
section[data-testid="stSidebar"] {{
    background-color: #0d0d14 !important;
    border-right: 1px solid #1e1e2e;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{
    color: {TEXT_PRIMARY} !important;
}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
    font-family: 'Syne', sans-serif !important;
    color: {TEXT_PRIMARY} !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, {ACCENT}, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.28) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.45) !important;
}}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {{
    background-color: {CARD_BG} !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 10px !important;
    color: {TEXT_PRIMARY} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}}
.stSelectbox > div > div {{
    background-color: {CARD_BG} !important;
    border-color: #2a2a3e !important;
    border-radius: 10px !important;
    color: {TEXT_PRIMARY} !important;
}}

/* Expander */
.stExpander {{
    background: {CARD_BG} !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 14px !important;
}}
.stExpander summary {{ font-family: 'Syne', sans-serif !important; color: {TEXT_PRIMARY} !important; }}

/* Progress */
.stProgress > div > div > div {{
    background: linear-gradient(90deg, {ACCENT}, #7c3aed) !important;
    border-radius: 99px !important;
}}
.stProgress > div > div {{
    background: #1e1e2e !important;
    border-radius: 99px !important;
}}

/* Metrics */
[data-testid="stMetricValue"] {{
    font-family: 'Syne', sans-serif !important;
    color: {ACCENT} !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED} !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {BG_DARK}; }}
::-webkit-scrollbar-thumb {{ background: #2a2a3e; border-radius: 99px; }}

/* ── Custom component styles ── */
.hb-card {{
    background: {CARD_BG};
    border: 1px solid #1e1e2e;
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.65rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.hb-card:hover {{
    transform: translateX(3px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    border-color: #2a2a3e;
}}
.hb-card-accent {{
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}}
.hb-title {{
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 1rem;
    color: {TEXT_PRIMARY};
}}
.hb-meta {{
    font-size: 0.76rem; color: {TEXT_MUTED}; margin-top: 2px;
}}
.hb-streak {{
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(251,146,60,0.13); color: #fb923c;
    border-radius: 99px; padding: 2px 9px;
    font-size: 0.73rem; font-weight: 700;
    font-family: 'Syne', sans-serif;
    border: 1px solid rgba(251,146,60,0.28);
}}
.hb-badge {{
    display: inline-flex; align-items: center;
    background: rgba(99,102,241,0.13); color: {ACCENT};
    border-radius: 99px; padding: 2px 9px;
    font-size: 0.73rem; font-weight: 700;
    font-family: 'Syne', sans-serif;
    border: 1px solid rgba(99,102,241,0.28);
    margin-left: 5px;
}}
.hb-stat {{
    background: {CARD_BG}; border: 1px solid #1e1e2e;
    border-radius: 16px; padding: 1.25rem 1rem; text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.hb-stat:hover {{
    border-color: rgba(99,102,241,0.35);
    box-shadow: 0 0 22px rgba(99,102,241,0.1);
}}
.hb-stat-num {{
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, {ACCENT}, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.1;
}}
.hb-stat-lbl {{
    font-size: 0.7rem; color: {TEXT_MUTED};
    text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px;
}}
.hb-section {{
    font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 800;
    color: {TEXT_PRIMARY}; margin: 1.1rem 0 0.65rem; letter-spacing: -0.02em;
}}
.hb-heatmap {{ display: flex; flex-wrap: wrap; gap: 2px; margin-top: 6px; }}
.hb-heatmap-cell {{ width: 13px; height: 13px; border-radius: 3px; }}
.hb-empty {{
    text-align: center; padding: 3rem 1rem; color: {TEXT_MUTED};
}}
.hb-page-title {{
    font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, {TEXT_PRIMARY} 40%, {ACCENT});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.15;
}}
.hb-page-sub {{
    font-size: 0.82rem; color: {TEXT_MUTED}; margin-top: 3px; margin-bottom: 1.4rem;
}}
.hb-done-btn button {{
    background: rgba(34,197,94,0.13) !important; color: #22c55e !important;
    box-shadow: none !important; border: 1px solid rgba(34,197,94,0.25) !important;
}}
.hb-done-btn button:hover {{
    background: rgba(34,197,94,0.25) !important;
    box-shadow: 0 2px 12px rgba(34,197,94,0.2) !important;
    transform: none !important;
}}
.hb-undo-btn button {{
    background: rgba(251,146,60,0.1) !important; color: #fb923c !important;
    box-shadow: none !important; border: 1px solid rgba(251,146,60,0.2) !important;
    transform: none !important;
}}
.hb-undo-btn button:hover {{ transform: none !important; }}
.hb-del-btn button {{
    background: rgba(239,68,68,0.1) !important; color: #ef4444 !important;
    box-shadow: none !important; border: 1px solid rgba(239,68,68,0.2) !important;
    transform: none !important;
}}
.hb-del-btn button:hover {{
    background: rgba(239,68,68,0.22) !important; transform: none !important;
}}
.hb-week-card {{
    background: {CARD_BG}; border: 1px solid #1e1e2e;
    border-radius: 14px; padding: 1rem 1.2rem; text-align: center;
}}
.hb-week-num {{
    font-family: 'Syne', sans-serif; font-size: 1.5rem;
    font-weight: 800; color: {ACCENT};
}}
.hb-week-lbl {{
    font-size: 0.68rem; color: {TEXT_MUTED};
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;
}}
.hb-week-sub {{ font-size: 0.7rem; color: #3a3a5a; margin-top: 3px; }}
</style>
""", unsafe_allow_html=True)


# ── Data helpers ──────────────────────────────────────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except Exception: return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def get_habits():    return load_json(HABITS_FILE, [])
def save_habits(h):  save_json(HABITS_FILE, h)
def get_logs():      return load_json(LOGS_FILE, {})
def save_logs(lg):   save_json(LOGS_FILE, lg)
def today_str():     return date.today().isoformat()

def toggle_log(habit_id):
    logs = get_logs()
    key = f"{habit_id}_{today_str()}"
    logs[key] = not logs.get(key, False)
    save_logs(logs)

def is_done_today(habit_id):
    return get_logs().get(f"{habit_id}_{today_str()}", False)

def compute_streak(habit_id, logs):
    streak, d = 0, date.today()
    while True:
        if logs.get(f"{habit_id}_{d.isoformat()}", False):
            streak += 1; d -= timedelta(days=1)
        else: break
    return streak

def completion_rate(habit_id, logs, days=30):
    count = sum(1 for i in range(days)
                if logs.get(f"{habit_id}_{(date.today()-timedelta(days=i)).isoformat()}", False))
    return count / days * 100

def get_badge(streak):
    badge = ""
    for t, n in sorted(BADGE_THRESHOLDS.items(), reverse=True):
        if streak >= t: badge = n; break
    return badge

def heatmap_html(habit_id, logs, weeks=16):
    cells, d = [], date.today() - timedelta(weeks=weeks)
    while d <= date.today():
        done  = logs.get(f"{habit_id}_{d.isoformat()}", False)
        color = "#6366f1" if done else "#1a1a2a"
        cells.append(f'<div class="hb-heatmap-cell" style="background:{color};" title="{d.isoformat()}"></div>')
        d += timedelta(days=1)
    return f'<div class="hb-heatmap">{"".join(cells)}</div>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:0.75rem 0 1.25rem;text-align:center;">
      <div style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;
                  background:linear-gradient(135deg,{ACCENT},#a78bfa);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        🔥 Habitify
      </div>
      <div style="font-size:0.68rem;color:#4a4a6a;letter-spacing:0.14em;margin-top:3px;">
        DISCIPLINE · CLARITY · GROWTH
      </div>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio("nav",
        ["🏠  Today", "➕  Add Habit", "📊  Analytics", "🏆  Achievements", "⚙️  Manage"],
        label_visibility="collapsed")
    page = nav.split("  ")[1]

    st.markdown("<hr style='border-color:#1e1e2e;margin:0.9rem 0'>", unsafe_allow_html=True)

    q_idx = int(hashlib.md5(today_str().encode()).hexdigest(), 16) % len(QUOTES)
    st.markdown(f"""
    <div style="font-size:0.75rem;color:#4a4a6a;font-style:italic;
                border-left:2px solid {ACCENT};padding-left:0.7rem;line-height:1.5;">
      "{QUOTES[q_idx]}"
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# TODAY
# ═════════════════════════════════════════════════════════════════════════
if page == "Today":
    st.markdown(f"""
    <div class="hb-page-title">Today's Dashboard</div>
    <div class="hb-page-sub">{date.today().strftime('%A, %B %d')} · Stay consistent, stay winning.</div>
    """, unsafe_allow_html=True)

    habits = get_habits()
    logs   = get_logs()

    if not habits:
        st.markdown("""
        <div class="hb-empty">
          <div style="font-size:2.8rem;margin-bottom:6px;">🌱</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;
                      color:#c0c0e0;margin-bottom:6px;">No habits yet</div>
          <div style="font-size:0.84rem;color:#6a6a8a;">Use <b>Add Habit</b> in the sidebar to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        done_today   = sum(1 for h in habits if is_done_today(h["id"]))
        total        = len(habits)
        pct          = done_today / total if total else 0
        best_streak  = max((compute_streak(h["id"], logs) for h in habits), default=0)
        avg_7        = sum(completion_rate(h["id"], logs, 7) for h in habits) / len(habits)
        all_time     = sum(1 for v in logs.values() if v)

        c1, c2, c3, c4 = st.columns(4)
        for col, num, lbl in [
            (c1, f"{done_today}/{total}", "Done Today"),
            (c2, f"🔥 {best_streak}",    "Best Streak"),
            (c3, f"{avg_7:.0f}%",        "7-Day Avg"),
            (c4, str(all_time),          "All-Time ✓"),
        ]:
            col.markdown(
                f'<div class="hb-stat"><div class="hb-stat-num">{num}</div>'
                f'<div class="hb-stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.88rem;color:{TEXT_PRIMARY};">
            Daily Progress</span>
          <span style="font-size:0.82rem;color:{ACCENT};font-weight:600;">
            {done_today} of {total} completed</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(pct)
        st.markdown("<br>", unsafe_allow_html=True)

        pending   = [h for h in habits if not is_done_today(h["id"])]
        completed = [h for h in habits if is_done_today(h["id"])]

        if pending:
            st.markdown('<div class="hb-section">⏳ Pending</div>', unsafe_allow_html=True)
            for h in pending:
                streak = compute_streak(h["id"], logs)
                badge  = get_badge(streak)
                color  = h.get("color", ACCENT)
                col_c, col_b = st.columns([5, 1])
                with col_c:
                    b_html = f'<span class="hb-badge">{badge}</span>' if badge else ""
                    n_html = (f'<div style="margin-top:5px;font-size:0.76rem;color:{TEXT_MUTED};">'
                              f'{h["note"]}</div>') if h.get("note") else ""
                    st.markdown(f"""
                    <div class="hb-card">
                      <div class="hb-card-accent" style="background:{color};"></div>
                      <div style="display:flex;align-items:center;gap:9px;flex-wrap:wrap;padding-left:8px;">
                        <span style="font-size:1.3rem;">{h.get("emoji","📌")}</span>
                        <div style="flex:1;">
                          <div class="hb-title">{h["name"]}</div>
                          <div class="hb-meta">{h.get("category","General")} · {h.get("frequency","Daily")}</div>
                        </div>
                        <div style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;">
                          <span class="hb-streak">🔥 {streak}d</span>{b_html}
                        </div>
                      </div>{n_html}
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="hb-done-btn">', unsafe_allow_html=True)
                    if st.button("✓ Done", key=f"done_{h['id']}"):
                        toggle_log(h["id"]); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        if completed:
            st.markdown('<div class="hb-section" style="margin-top:1.4rem;">✅ Completed</div>',
                        unsafe_allow_html=True)
            for h in completed:
                streak = compute_streak(h["id"], logs)
                col_c, col_b = st.columns([5, 1])
                with col_c:
                    st.markdown(f"""
                    <div class="hb-card" style="opacity:0.65;">
                      <div class="hb-card-accent" style="background:#22c55e;"></div>
                      <div style="display:flex;align-items:center;gap:9px;padding-left:8px;">
                        <span style="font-size:1.3rem;">{h.get("emoji","✅")}</span>
                        <div style="flex:1;">
                          <div class="hb-title" style="text-decoration:line-through;opacity:0.6;">{h["name"]}</div>
                          <div class="hb-meta">{h.get("category","General")}</div>
                        </div>
                        <span class="hb-streak" style="background:rgba(34,197,94,0.13);color:#22c55e;
                              border-color:rgba(34,197,94,0.28);">🔥 {streak}d</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="hb-undo-btn">', unsafe_allow_html=True)
                    if st.button("↩ Undo", key=f"undo_{h['id']}"):
                        toggle_log(h["id"]); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# ADD HABIT
# ═════════════════════════════════════════════════════════════════════════
elif page == "Add Habit":
    st.markdown(f"""
    <div class="hb-page-title">Add New Habit</div>
    <div class="hb-page-sub">Small consistent actions compound into extraordinary results.</div>
    """, unsafe_allow_html=True)

    COLOR_MAP = {
        "#6366f1":"Indigo", "#22c55e":"Green", "#f59e0b":"Amber",
        "#ec4899":"Pink",   "#14b8a6":"Teal",  "#f97316":"Orange",
        "#8b5cf6":"Violet", "#06b6d4":"Cyan",
    }

    with st.form("add_form", clear_on_submit=True):
        r1, r2 = st.columns([4, 1])
        with r1: name  = st.text_input("Habit Name *", placeholder="e.g. Morning Meditation")
        with r2: emoji = st.text_input("Emoji", placeholder="🧘", max_chars=4)

        r3, r4 = st.columns(2)
        with r3: category  = st.selectbox("Category", ["Health & Fitness","Mind & Learning",
                                "Productivity","Relationships","Finance","Creativity","Spirituality","Other"])
        with r4: frequency = st.selectbox("Frequency", ["Daily","Weekdays","Weekends","3x/Week"])

        r5, r6 = st.columns(2)
        with r5:
            color_label = st.selectbox("Colour Theme", list(COLOR_MAP.values()))
            color_hex   = [k for k, v in COLOR_MAP.items() if v == color_label][0]
        with r6:
            target_days = st.slider("Weekly target (days)", 1, 7, 7)

        note = st.text_area("Motivation / Note",
                            placeholder="Why does this habit matter to you?", height=75)

        if st.form_submit_button("➕  Add Habit", use_container_width=True):
            if not name.strip():
                st.error("Please enter a habit name.")
            else:
                habits = get_habits()
                habits.append({
                    "id": str(uuid.uuid4())[:8],
                    "name": name.strip(),
                    "emoji": emoji.strip() or "📌",
                    "category": category,
                    "frequency": frequency,
                    "color": color_hex,
                    "note": note.strip(),
                    "target_days": target_days,
                    "created": today_str(),
                })
                save_habits(habits)
                st.success(f"✅ '{name.strip()}' added! Head to Today to start tracking.")
                st.balloons()


# ═════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═════════════════════════════════════════════════════════════════════════
elif page == "Analytics":
    st.markdown(f"""
    <div class="hb-page-title">Analytics</div>
    <div class="hb-page-sub">Understand your patterns. Optimise your performance.</div>
    """, unsafe_allow_html=True)

    habits = get_habits()
    logs   = get_logs()

    if not habits:
        st.markdown('<div class="hb-empty"><div style="font-size:2.8rem;">📊</div>'
                    '<div style="color:#6a6a8a;font-size:0.84rem;margin-top:6px;">'
                    'Add habits first to see analytics.</div></div>', unsafe_allow_html=True)
    else:
        period = st.select_slider("Analysis Period",
                                  options=[7, 14, 30, 60, 90], value=30,
                                  format_func=lambda x: f"{x} days")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="hb-section">Per-Habit Performance</div>', unsafe_allow_html=True)

        for h in habits:
            rate   = completion_rate(h["id"], logs, period)
            streak = compute_streak(h["id"], logs)
            color  = h.get("color", ACCENT)
            with st.expander(f"{h.get('emoji','📌')}  {h['name']}  —  {rate:.0f}% ({period}d)"):
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Completion Rate", f"{rate:.1f}%")
                cc2.metric("Current Streak",  f"🔥 {streak}d")
                total_done = sum(1 for k, v in logs.items() if k.startswith(h["id"]) and v)
                cc3.metric("All-Time ✓", total_done)

                st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED};text-transform:uppercase;"
                             f"letter-spacing:0.08em;margin:0.75rem 0 4px;'>16-Week Heatmap</div>",
                             unsafe_allow_html=True)
                st.markdown(heatmap_html(h["id"], logs), unsafe_allow_html=True)

                st.markdown(f"<div style='font-size:0.72rem;color:{TEXT_MUTED};text-transform:uppercase;"
                             f"letter-spacing:0.08em;margin:0.85rem 0 4px;'>Last 7 Days</div>",
                             unsafe_allow_html=True)
                labels, vals = [], []
                for i in range(6, -1, -1):
                    d = date.today() - timedelta(days=i)
                    labels.append(d.strftime("%a"))
                    vals.append(1 if logs.get(f"{h['id']}_{d.isoformat()}", False) else 0)

                bar = '<div style="display:flex;gap:5px;align-items:flex-end;height:52px;">'
                for lbl, val in zip(labels, vals):
                    bg = color if val else "#1a1a2a"
                    ht = "100%" if val else "18%"
                    bar += (f'<div style="flex:1;display:flex;flex-direction:column;'
                            f'align-items:center;gap:3px;">'
                            f'<div style="width:100%;height:{ht};background:{bg};border-radius:4px;"></div>'
                            f'<span style="font-size:0.62rem;color:{TEXT_MUTED};">{lbl}</span></div>')
                bar += '</div>'
                st.markdown(bar, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="hb-section">Weekly Overview — Last 4 Weeks</div>',
                    unsafe_allow_html=True)
        wcols = st.columns(4)
        for w in range(4):
            done = sum(
                1 for i in range(7) for h in habits
                if logs.get(f"{h['id']}_{(date.today()-timedelta(weeks=w,days=i)).isoformat()}", False)
            )
            tw   = len(habits) * 7
            pctw = done / tw * 100 if tw else 0
            lbl  = "This Week" if w == 0 else f"Week -{w}"
            wcols[w].markdown(
                f'<div class="hb-week-card"><div class="hb-week-num">{pctw:.0f}%</div>'
                f'<div class="hb-week-lbl">{lbl}</div>'
                f'<div class="hb-week-sub">{done}/{tw} done</div></div>',
                unsafe_allow_html=True
            )


# ═════════════════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ═════════════════════════════════════════════════════════════════════════
elif page == "Achievements":
    st.markdown(f"""
    <div class="hb-page-title">Achievements</div>
    <div class="hb-page-sub">Every streak tells a story of discipline earned.</div>
    """, unsafe_allow_html=True)

    habits = get_habits()
    logs   = get_logs()

    BADGES = {
        "🌱 Seedling": ("You've begun your journey.",            "#22c55e", 3),
        "🔥 On Fire":  ("7 days strong — momentum is building!","#f97316", 7),
        "⚡ Spartan":  ("14 days of iron discipline.",           "#6366f1", 14),
        "💎 Diamond":  ("30 days — you are unstoppable.",        "#06b6d4", 30),
        "🚀 Elite":    ("60 days. Most people quit long ago.",   "#8b5cf6", 60),
        "🏆 Legend":   ("100 days. You have rewritten yourself.","#f59e0b", 100),
    }

    earned = {get_badge(compute_streak(h["id"], logs)) for h in habits} - {""}

    cols = st.columns(3)
    for i, (badge, (desc, color, threshold)) in enumerate(BADGES.items()):
        icon = badge.split()[0]
        name = badge.split(" ", 1)[1]
        unlocked = badge in earned
        with cols[i % 3]:
            if unlocked:
                st.markdown(f"""
                <div style="background:{CARD_BG};border:1px solid {color}44;border-radius:18px;
                            padding:1.4rem;text-align:center;box-shadow:0 0 22px {color}2a;
                            margin-bottom:0.9rem;">
                  <div style="font-size:2.3rem;margin-bottom:6px;">{icon}</div>
                  <div style="font-family:'Syne',sans-serif;font-weight:700;color:{color};
                              font-size:0.92rem;">{name}</div>
                  <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:3px;">{desc}</div>
                  <div style="margin-top:10px;font-size:0.7rem;background:{color}20;color:{color};
                              border-radius:99px;padding:2px 12px;display:inline-block;
                              font-weight:700;">UNLOCKED ✓</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#0c0c16;border:1px solid #1a1a2a;border-radius:18px;
                            padding:1.4rem;text-align:center;opacity:0.42;margin-bottom:0.9rem;">
                  <div style="font-size:2.3rem;margin-bottom:6px;filter:grayscale(1);">{icon}</div>
                  <div style="font-family:'Syne',sans-serif;font-weight:700;color:#3a3a5a;
                              font-size:0.92rem;">{name}</div>
                  <div style="font-size:0.75rem;color:#2e2e4a;margin-top:3px;">{desc}</div>
                  <div style="margin-top:10px;font-size:0.7rem;background:#1a1a2a;color:#3a3a5a;
                              border-radius:99px;padding:2px 12px;display:inline-block;">
                    🔒 {threshold}-day streak
                  </div>
                </div>
                """, unsafe_allow_html=True)

    if habits:
        st.markdown('<div class="hb-section" style="margin-top:1.2rem;">🏅 Habit Leaderboard</div>',
                    unsafe_allow_html=True)
        ranked = sorted(habits, key=lambda h: compute_streak(h["id"], logs), reverse=True)
        for rank, h in enumerate(ranked, 1):
            streak = compute_streak(h["id"], logs)
            rate   = completion_rate(h["id"], logs, 30)
            medal  = ["🥇","🥈","🥉"][rank-1] if rank <= 3 else f"#{rank}"
            st.markdown(f"""
            <div class="hb-card">
              <div class="hb-card-accent" style="background:{h.get('color',ACCENT)};"></div>
              <div style="display:flex;align-items:center;gap:10px;padding-left:8px;">
                <span style="font-size:1.3rem;min-width:28px;text-align:center;">{medal}</span>
                <span style="font-size:1.2rem;">{h.get("emoji","📌")}</span>
                <div style="flex:1;">
                  <div class="hb-title">{h["name"]}</div>
                  <div class="hb-meta">{h.get("category","General")}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:'Syne',sans-serif;font-weight:700;color:#fb923c;
                              font-size:0.9rem;">🔥 {streak}d streak</div>
                  <div style="font-size:0.72rem;color:{TEXT_MUTED};">{rate:.0f}% last 30d</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# MANAGE
# ═════════════════════════════════════════════════════════════════════════
elif page == "Manage":
    st.markdown(f"""
    <div class="hb-page-title">Manage Habits</div>
    <div class="hb-page-sub">Edit or remove habits from your tracker.</div>
    """, unsafe_allow_html=True)

    habits = get_habits()
    logs   = get_logs()

    if not habits:
        st.markdown('<div class="hb-empty"><div style="font-size:2.8rem;">⚙️</div>'
                    '<div style="color:#6a6a8a;font-size:0.84rem;margin-top:6px;">'
                    'No habits to manage yet.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.82rem;margin-bottom:0.8rem;'>"
                    f"You have <b style='color:{ACCENT}'>{len(habits)}</b> habits tracked.</p>",
                    unsafe_allow_html=True)

        to_delete = None
        for h in habits:
            streak = compute_streak(h["id"], logs)
            col_c, col_d = st.columns([6, 1])
            with col_c:
                n_html = (f'<div style="margin-top:5px;font-size:0.75rem;color:{TEXT_MUTED};">'
                          f'📝 {h["note"]}</div>') if h.get("note") else ""
                st.markdown(f"""
                <div class="hb-card">
                  <div class="hb-card-accent" style="background:{h.get('color',ACCENT)};"></div>
                  <div style="display:flex;align-items:center;gap:9px;padding-left:8px;flex-wrap:wrap;">
                    <span style="font-size:1.2rem;">{h.get("emoji","📌")}</span>
                    <div style="flex:1;">
                      <div class="hb-title">{h["name"]}</div>
                      <div class="hb-meta">{h.get("category","General")} · {h.get("frequency","Daily")}
                           · Added {h.get("created","—")}</div>
                    </div>
                    <span class="hb-streak">🔥 {streak}d</span>
                  </div>{n_html}
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                st.markdown('<div class="hb-del-btn">', unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{h['id']}", help="Delete this habit"):
                    to_delete = h["id"]
                st.markdown('</div>', unsafe_allow_html=True)

        if to_delete:
            save_habits([h for h in habits if h["id"] != to_delete])
            st.success("Habit removed.")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️  Clear All Logs (keep habits)", type="secondary"):
            save_logs({})
            st.success("All logs cleared.")
            st.rerun()
