"""
app.py  —  Habitforge
Professional habit & discipline tracker with public username system,
community challenges, global leaderboard, and mobile-native design.
"""
import streamlit as st
import hashlib
from datetime import date, timedelta
import db
import styles as S

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habitforge",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",   # mobile-friendly default
)
st.markdown(S.get_css(), unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, val in {
    "user": None,
    "auth_tab": "login",
    "page": "today",
    "msg": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def uid() -> str:
    return st.session_state.user["id"]

def uname() -> str:
    return st.session_state.user["display_name"]

def set_page(p: str):
    st.session_state.page = p

def heatmap(user_id: str, habit_id: str, weeks: int = 13) -> str:
    logs = db.get_logs(user_id)
    cells, d = [], date.today() - timedelta(weeks=weeks)
    while d <= date.today():
        done = logs.get(f"{habit_id}_{d.isoformat()}", False)
        col  = "#e8c547" if done else "#1c1c2e"
        cells.append(f'<div class="hf-hm-cell" style="background:{col};" title="{d}"></div>')
        d += timedelta(days=1)
    return f'<div class="hf-heatmap">{"".join(cells)}</div>'

def avatar(display_name: str, seed: str, size: int = 36) -> str:
    color    = S.avatar_color(seed)
    initials = S.avatar_initials(display_name)
    return (f'<div class="hf-avatar" style="background:{color};width:{size}px;height:{size}px;">'
            f'{initials}</div>')

def medal(rank: int) -> str:
    return ["🥇","🥈","🥉"][rank-1] if rank <= 3 else f"<b style='color:{S.MUTED}'>#{rank}</b>"

def quote_of_day() -> str:
    idx = int(hashlib.md5(db.today().encode()).hexdigest(), 16) % len(S.QUOTES)
    return S.QUOTES[idx]

# ─────────────────────────────────────────────────────────────────────────────
# AUTH SCREENS
# ─────────────────────────────────────────────────────────────────────────────
def auth_screen():
    # Centred logo
    st.markdown(f"""
    <div style="text-align:center;padding:2.5rem 0 1rem;">
      <div class="hf-wordmark">⚡ Habitforge</div>
      <div class="hf-wordmark-sub">Build the life you deserve</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                uname = st.text_input("Username", placeholder="your_username")
                pw    = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    ok, msg, user = db.login(uname, pw)
                    if ok:
                        st.session_state.user = user
                        st.session_state.page = "today"
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("reg_form"):
                disp  = st.text_input("Display Name", placeholder="e.g. Alex Morgan")
                uname = st.text_input("Username", placeholder="alex_morgan  (letters, numbers, _ -)").lower()
                pw    = st.text_input("Password", type="password", placeholder="min. 6 characters")
                pw2   = st.text_input("Confirm Password", type="password", placeholder="repeat password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if pw != pw2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = db.register(uname, pw, disp)
                        if ok:
                            _, _, user = db.login(uname, pw)
                            st.session_state.user = user
                            st.session_state.page = "today"
                            st.success("Account created! Welcome 🎉")
                            st.rerun()
                        else:
                            st.error(msg)

    # Social proof strip
    users     = db.get_users()
    user_count= len(users)
    st.markdown(f"""
    <div style="text-align:center;margin-top:2.5rem;padding-bottom:1rem;">
      <span style="font-size:0.78rem;color:{S.MUTED};">
        Join <b style="color:{S.ACCENT};">{user_count}</b> people already building better habits
      </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAV
# ─────────────────────────────────────────────────────────────────────────────
def sidebar():
    user = st.session_state.user
    with st.sidebar:
        # Wordmark
        st.markdown(f"""
        <div style="padding:1rem 0 1.2rem;">
          <div class="hf-wordmark">⚡ Habitforge</div>
          <div class="hf-wordmark-sub">Personal discipline OS</div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        col_av, col_info = st.columns([1, 3])
        with col_av:
            st.markdown(avatar(user["display_name"], user["username"], size=40),
                        unsafe_allow_html=True)
        with col_info:
            score = db.user_score(uid())
            st.markdown(f"""
            <div style="font-family:'Outfit',sans-serif;line-height:1.3;">
              <div style="font-weight:700;font-size:0.92rem;color:{S.TEXT};">{user['display_name']}</div>
              <div style="font-size:0.7rem;color:{S.MUTED};">@{user['username']}</div>
              <div style="font-size:0.7rem;color:{S.ACCENT};font-weight:600;">⚡ {score:,} pts</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"<hr class='hf-divider'>", unsafe_allow_html=True)

        # Navigation
        PAGES = {
            "today":       "🏠  Today",
            "add":         "➕  Add Habit",
            "analytics":   "📊  Analytics",
            "challenges":  "🏆  Challenges",
            "leaderboard": "🌍  Leaderboard",
            "profile":     "👤  Profile",
        }
        for key, label in PAGES.items():
            active = st.session_state.page == key
            btn_style = (f"background:rgba(232,197,71,0.12);color:{S.ACCENT};"
                         f"border-left:2px solid {S.ACCENT};" if active
                         else f"color:{S.MUTED};")
            st.markdown(
                f'<div style="{btn_style}border-radius:9px;padding:0.45rem 0.75rem;'
                f'font-family:\'Outfit\',sans-serif;font-size:0.875rem;font-weight:600;'
                f'cursor:pointer;margin-bottom:2px;">{label}</div>',
                unsafe_allow_html=True
            )
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         help=label.split("  ")[1]):
                set_page(key); st.rerun()

        st.markdown(f"<hr class='hf-divider'>", unsafe_allow_html=True)

        # Quote of day
        st.markdown(f"""
        <div style="font-size:0.72rem;color:{S.MUTED};font-style:italic;
                    border-left:2px solid {S.ACCENT};padding-left:0.65rem;
                    line-height:1.55;">"{quote_of_day()}"</div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "today"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TODAY
# ─────────────────────────────────────────────────────────────────────────────
def page_today():
    user_id = uid()
    habits  = db.get_habits(user_id)
    logs    = db.get_logs(user_id)

    st.markdown(f"""
    <div class="hf-page-title">Good {_greeting()}, {uname().split()[0]}.</div>
    <div class="hf-page-sub">{date.today().strftime('%A, %B %d, %Y')}</div>
    """, unsafe_allow_html=True)

    if not habits:
        st.markdown(f"""
        <div style="text-align:center;padding:3rem 1rem;color:{S.MUTED};">
          <div style="font-size:2.5rem;margin-bottom:10px;">🌱</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                      color:{S.TEXT};margin-bottom:6px;">No habits yet</div>
          <div style="font-size:0.84rem;">Add your first habit to begin your streak.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Add Your First Habit"):
            set_page("add"); st.rerun()
        return

    # ── Stat row ──
    done_today  = sum(1 for h in habits if db.is_done_today(user_id, h["id"]))
    total       = len(habits)
    pct         = done_today / total if total else 0
    best_s      = db.best_streak_across(user_id)
    avg_7       = sum(db.completion_rate(user_id, h["id"], 7) for h in habits) / len(habits)
    all_time    = db.total_completions(user_id)

    c1, c2, c3, c4 = st.columns(4)
    for col, n, l in [
        (c1, f"{done_today}/{total}", "Done Today"),
        (c2, f"🔥 {best_s}",          "Best Streak"),
        (c3, f"{avg_7:.0f}%",         "7-Day Avg"),
        (c4, f"{all_time:,}",         "All-Time ✓"),
    ]:
        col.markdown(f'<div class="hf-stat"><div class="hf-stat-n">{n}</div>'
                     f'<div class="hf-stat-l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
      <span style="font-family:'Outfit',sans-serif;font-weight:600;
                   font-size:0.82rem;color:{S.TEXT};">Daily Progress</span>
      <span style="font-size:0.82rem;color:{S.ACCENT};font-weight:700;">
        {done_today}/{total} · {pct*100:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)
    st.progress(pct)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Habit lists ──
    pending   = [h for h in habits if not db.is_done_today(user_id, h["id"])]
    completed = [h for h in habits if db.is_done_today(user_id, h["id"])]

    if pending:
        st.markdown('<div class="hf-section">⏳ Pending</div>', unsafe_allow_html=True)
        for h in pending:
            s     = db.streak(user_id, h["id"])
            badge = S.get_badge(s)
            color = h.get("color", S.ACCENT)
            cc, cb = st.columns([5, 1])
            with cc:
                b_html = f'<span class="hf-pill hf-pill-gold">{badge}</span>' if badge else ""
                n_html = (f'<div style="margin-top:5px;font-size:0.75rem;color:{S.MUTED};">'
                          f'{h["note"]}</div>') if h.get("note") else ""
                st.markdown(f"""
                <div class="hf-card">
                  <div class="hf-card-bar" style="background:{color};"></div>
                  <div style="display:flex;align-items:center;gap:10px;
                              padding-left:10px;flex-wrap:wrap;">
                    <span style="font-size:1.35rem;">{h.get("emoji","📌")}</span>
                    <div style="flex:1;min-width:0;">
                      <div style="font-family:'Outfit',sans-serif;font-weight:700;
                                  font-size:0.96rem;color:{S.TEXT};
                                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        {h["name"]}</div>
                      <div style="font-size:0.73rem;color:{S.MUTED};margin-top:1px;">
                        {h.get("category","General")} · {h.get("frequency","Daily")}</div>
                    </div>
                    <div style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;">
                      <span class="hf-pill hf-pill-gold">🔥 {s}d</span>{b_html}
                    </div>
                  </div>{n_html}
                </div>
                """, unsafe_allow_html=True)
            with cb:
                st.markdown('<div class="hf-btn-green">', unsafe_allow_html=True)
                if st.button("✓", key=f"done_{h['id']}", help="Mark done"):
                    db.toggle_log(user_id, h["id"]); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    if completed:
        st.markdown('<div class="hf-section" style="margin-top:1.2rem;">✅ Completed</div>',
                    unsafe_allow_html=True)
        for h in completed:
            s = db.streak(user_id, h["id"])
            cc, cb = st.columns([5, 1])
            with cc:
                st.markdown(f"""
                <div class="hf-card" style="opacity:0.55;">
                  <div class="hf-card-bar" style="background:{S.ACCENT2};"></div>
                  <div style="display:flex;align-items:center;gap:10px;
                              padding-left:10px;">
                    <span style="font-size:1.3rem;">{h.get("emoji","✅")}</span>
                    <div style="flex:1;">
                      <div style="font-family:'Outfit',sans-serif;font-weight:700;
                                  font-size:0.96rem;color:{S.TEXT};
                                  text-decoration:line-through;opacity:0.6;">
                        {h["name"]}</div>
                      <div style="font-size:0.73rem;color:{S.MUTED};">
                        {h.get("category","General")}</div>
                    </div>
                    <span class="hf-pill hf-pill-green">🔥 {s}d</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with cb:
                st.markdown('<div class="hf-btn-amber">', unsafe_allow_html=True)
                if st.button("↩", key=f"undo_{h['id']}", help="Undo"):
                    db.toggle_log(user_id, h["id"]); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # If everything done — celebration message
    if done_today == total and total > 0:
        st.markdown(f"""
        <div style="text-align:center;margin-top:1.5rem;padding:1.5rem;
                    background:rgba(74,222,128,0.07);border:1px solid rgba(74,222,128,0.2);
                    border-radius:16px;">
          <div style="font-size:2rem;">🏆</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                      color:{S.ACCENT2};font-weight:700;margin:6px 0;">
            Perfect Day!</div>
          <div style="font-size:0.82rem;color:{S.MUTED};">
            You completed all {total} habits today. Incredible discipline.</div>
        </div>
        """, unsafe_allow_html=True)

def _greeting() -> str:
    h = date.today().timetuple().tm_hour
    if h < 12: return "morning"
    if h < 17: return "afternoon"
    return "evening"


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ADD HABIT
# ─────────────────────────────────────────────────────────────────────────────
def page_add():
    st.markdown(f"""
    <div class="hf-page-title">Add New Habit</div>
    <div class="hf-page-sub">Small consistent actions compound into extraordinary results.</div>
    """, unsafe_allow_html=True)

    with st.form("add_form", clear_on_submit=True):
        r1, r2 = st.columns([4, 1])
        with r1: name  = st.text_input("Habit Name *", placeholder="e.g. Morning Meditation")
        with r2: emoji = st.text_input("Emoji", placeholder="🧘", max_chars=4)

        r3, r4 = st.columns(2)
        with r3:
            category = st.selectbox("Category", [
                "Health & Fitness","Mind & Learning","Productivity",
                "Relationships","Finance","Creativity","Spirituality","Other"
            ])
        with r4:
            frequency = st.selectbox("Frequency",
                                     ["Daily","Weekdays","Weekends","3× / Week","Custom"])

        r5, r6 = st.columns(2)
        with r5:
            color_label = st.selectbox("Colour", list(S.COLOR_MAP.values()))
            color_hex   = [k for k, v in S.COLOR_MAP.items() if v == color_label][0]
        with r6:
            target_days = st.slider("Weekly target (days)", 1, 7, 7)

        note = st.text_area("Your Why  (optional)",
                            placeholder="Why does this habit matter to you?", height=70)

        if st.form_submit_button("Add Habit →", use_container_width=True):
            if not name.strip():
                st.error("Habit name is required.")
            else:
                db.add_habit(uid(), name, emoji or "📌", category,
                             frequency, color_hex, note, target_days)
                st.success(f"✅ '{name.strip()}' added! Track it in Today.")
                st.balloons()

    # Quick tips
    st.markdown(f"""
    <div style="margin-top:1.8rem;padding:1.1rem 1.3rem;
                background:{S.CARD};border:1px solid {S.BORDER};border-radius:14px;">
      <div style="font-family:'Playfair Display',serif;font-weight:700;
                  color:{S.TEXT};margin-bottom:8px;">💡 Habit-building tips</div>
      <div style="font-size:0.8rem;color:{S.MUTED};line-height:1.7;">
        • <b style="color:{S.TEXT};">Start tiny</b> — 2 minutes beats 0 minutes every time.<br>
        • <b style="color:{S.TEXT};">Stack habits</b> — attach new habits to existing ones.<br>
        • <b style="color:{S.TEXT};">Track every day</b> — streaks create powerful momentum.<br>
        • <b style="color:{S.TEXT};">Join a challenge</b> — community accountability 3× your success rate.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
def page_analytics():
    user_id = uid()
    habits  = db.get_habits(user_id)
    logs    = db.get_logs(user_id)

    st.markdown(f"""
    <div class="hf-page-title">Analytics</div>
    <div class="hf-page-sub">Understand your patterns. Optimise your performance.</div>
    """, unsafe_allow_html=True)

    if not habits:
        st.info("Add habits first to see your analytics.")
        return

    period = st.select_slider("Analysis Period",
                              options=[7, 14, 30, 60, 90], value=30,
                              format_func=lambda x: f"{x} days")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Overview stats ──
    c1, c2, c3, c4 = st.columns(4)
    total_done  = db.total_completions(user_id)
    best_s      = db.best_streak_across(user_id)
    avg_rate    = sum(db.completion_rate(user_id, h["id"], period) for h in habits) / len(habits)
    score       = db.user_score(user_id)
    for col, n, l in [
        (c1, f"{total_done:,}", "Total Completions"),
        (c2, f"🔥 {best_s}d",  "Best Streak"),
        (c3, f"{avg_rate:.0f}%",f"{period}d Avg Rate"),
        (c4, f"⚡ {score:,}",  "Your Score"),
    ]:
        col.markdown(f'<div class="hf-stat"><div class="hf-stat-n">{n}</div>'
                     f'<div class="hf-stat-l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="hf-section">Per-Habit Breakdown</div>', unsafe_allow_html=True)

    for h in habits:
        rate  = db.completion_rate(user_id, h["id"], period)
        s     = db.streak(user_id, h["id"])
        color = h.get("color", S.ACCENT)
        with st.expander(f"{h.get('emoji','📌')}  {h['name']}  ·  {rate:.0f}%  ·  🔥{s}d"):
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Completion Rate",  f"{rate:.1f}%")
            cc2.metric("Current Streak",   f"🔥 {s} days")
            td = sum(1 for k, v in logs.items() if k.startswith(h["id"]) and v)
            cc3.metric("All-Time ✓", td)

            # Heatmap
            st.markdown(f"<div class='hf-label' style='margin:0.8rem 0 4px;'>13-Week Heatmap</div>",
                        unsafe_allow_html=True)
            st.markdown(heatmap(user_id, h["id"]), unsafe_allow_html=True)

            # 7-day bar
            st.markdown(f"<div class='hf-label' style='margin:0.85rem 0 6px;'>Last 7 Days</div>",
                        unsafe_allow_html=True)
            days_l, days_v = [], []
            for i in range(6, -1, -1):
                d = date.today() - timedelta(days=i)
                days_l.append(d.strftime("%a"))
                days_v.append(1 if logs.get(f"{h['id']}_{d.isoformat()}", False) else 0)

            bar = '<div style="display:flex;gap:5px;align-items:flex-end;height:50px;">'
            for lbl, val in zip(days_l, days_v):
                bg = color if val else "#1c1c2e"
                ht = "100%" if val else "16%"
                bar += (f'<div style="flex:1;display:flex;flex-direction:column;'
                        f'align-items:center;gap:3px;">'
                        f'<div style="width:100%;height:{ht};background:{bg};'
                        f'border-radius:4px;transition:height 0.3s;"></div>'
                        f'<span style="font-size:0.6rem;color:{S.MUTED};">{lbl}</span></div>')
            bar += '</div>'
            st.markdown(bar, unsafe_allow_html=True)

    # ── 4-week overview ──
    st.markdown('<div class="hf-section">Weekly Overview</div>', unsafe_allow_html=True)
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
            f'<div class="hf-stat"><div class="hf-stat-n">{pctw:.0f}%</div>'
            f'<div class="hf-stat-l">{lbl}</div>'
            f'<div style="font-size:0.68rem;color:{S.MUTED};margin-top:3px;">'
            f'{done}/{tw}</div></div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CHALLENGES
# ─────────────────────────────────────────────────────────────────────────────
def page_challenges():
    user_id    = uid()
    challenges = db.get_challenges()
    enrolled   = {e["challenge_id"] for e in db.get_enrollments(user_id)}

    st.markdown(f"""
    <div class="hf-page-title">Community Challenges</div>
    <div class="hf-page-sub">
      Join a challenge, stay accountable, climb the board. 
      <b style="color:{S.ACCENT3};">{len(challenges)}</b> active challenges.
    </div>
    """, unsafe_allow_html=True)

    # Enrolled challenges first
    my_challenges = [c for c in challenges if c["id"] in enrolled]
    other         = [c for c in challenges if c["id"] not in enrolled]

    if my_challenges:
        st.markdown('<div class="hf-section">🎯 Your Active Challenges</div>',
                    unsafe_allow_html=True)
        for c in my_challenges:
            _challenge_card(c, user_id, enrolled=True)

    st.markdown('<div class="hf-section">🌍 All Challenges</div>',
                unsafe_allow_html=True)

    for c in other:
        _challenge_card(c, user_id, enrolled=False)


def _challenge_card(c: dict, user_id: str, enrolled: bool):
    color       = c.get("color", S.ACCENT3)
    enrolled_cls = "hf-challenge-enrolled" if enrolled else ""
    lb          = db.challenge_leaderboard(c["id"], top_n=3)
    top_names   = " · ".join(r["display_name"] for r in lb[:3]) if lb else "—"
    participants = c.get("participants", 0)

    col_c, col_b = st.columns([5, 1])
    with col_c:
        st.markdown(f"""
        <div class="hf-challenge {enrolled_cls}">
          <div style="position:absolute;top:0;left:0;width:3px;height:100%;
                      background:{color};border-radius:3px 0 0 3px;"></div>
          <div style="display:flex;align-items:flex-start;gap:12px;padding-left:10px;">
            <span style="font-size:1.7rem;margin-top:2px;">{c.get("emoji","🏆")}</span>
            <div style="flex:1;min-width:0;">
              <div style="font-family:'Playfair Display',serif;font-weight:700;
                          font-size:1rem;color:{S.TEXT};">{c["title"]}</div>
              <div style="font-size:0.77rem;color:{S.MUTED};margin-top:3px;line-height:1.5;">
                {c["description"]}</div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;align-items:center;">
                <span class="hf-pill hf-pill-sky">⏱ {c["duration_days"]}d</span>
                <span class="hf-pill hf-pill-sky">🎯 {c["category"]}</span>
                <span class="hf-pill hf-pill-sky">👥 {participants}</span>
                {'<span class="hf-pill hf-pill-green">✓ Enrolled</span>' if enrolled else ''}
              </div>
              <div style="font-size:0.7rem;color:{S.MUTED};margin-top:6px;">
                🏅 Top: {top_names}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        if enrolled:
            st.markdown('<div class="hf-btn-red">', unsafe_allow_html=True)
            if st.button("Leave", key=f"leave_{c['id']}"):
                db.unenroll(user_id, c["id"]); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="hf-btn-sky">', unsafe_allow_html=True)
            if st.button("Join", key=f"join_{c['id']}"):
                db.enroll(user_id, c["id"]); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Challenge-specific leaderboard inside expander
    with st.expander(f"📊  {c['title']} Leaderboard"):
        lb = db.challenge_leaderboard(c["id"], top_n=10)
        if not lb:
            st.markdown(f"<span style='color:{S.MUTED};font-size:0.82rem;'>"
                        "Be the first to join this challenge!</span>",
                        unsafe_allow_html=True)
        else:
            for i, r in enumerate(lb, 1):
                is_me = r["username"] == st.session_state.user["username"]
                me_cls = "hf-lb-me" if is_me else ""
                st.markdown(f"""
                <div class="hf-lb-row {me_cls}">
                  <span style="font-size:1.1rem;min-width:28px;text-align:center;">
                    {medal(i)}</span>
                  {avatar(r['display_name'], r['username'], 30)}
                  <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:0.88rem;color:{S.TEXT};
                                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                      {r['display_name']}
                      {'<span style="color:'+S.ACCENT+';font-size:0.7rem;"> · you</span>' if is_me else ''}
                    </div>
                    <div style="font-size:0.7rem;color:{S.MUTED};">@{r['username']}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-weight:700;font-size:0.88rem;color:{S.ACCENT};">
                      🔥 {r['best_streak']}d</div>
                    <div style="font-size:0.68rem;color:{S.MUTED};">
                      ⚡ {r['score']:,} pts</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GLOBAL LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def page_leaderboard():
    st.markdown(f"""
    <div class="hf-page-title">Global Leaderboard</div>
    <div class="hf-page-sub">The most disciplined people on Habitforge — ranked by score.</div>
    """, unsafe_allow_html=True)

    lb = db.global_leaderboard(top_n=50)
    me = st.session_state.user["username"]

    if not lb:
        st.info("No users yet — be the first!")
        return

    # My rank
    my_rank = next((i+1 for i, r in enumerate(lb) if r["username"] == me), None)
    if my_rank:
        st.markdown(f"""
        <div style="background:rgba(232,197,71,0.07);border:1px solid rgba(232,197,71,0.25);
                    border-radius:14px;padding:1rem 1.2rem;margin-bottom:1.2rem;
                    display:flex;align-items:center;gap:12px;">
          <div style="font-size:1.5rem;">{medal(my_rank)}</div>
          <div>
            <div style="font-family:'Playfair Display',serif;font-weight:700;
                        font-size:1rem;color:{S.ACCENT};">Your Global Rank</div>
            <div style="font-size:0.78rem;color:{S.MUTED};">
              #{my_rank} of {len(lb)} ranked users</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Column headers
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:0.3rem 1rem;
                font-size:0.65rem;color:{S.MUTED};text-transform:uppercase;
                letter-spacing:0.1em;font-family:'Outfit',sans-serif;font-weight:600;">
      <span style="min-width:28px;">#</span>
      <span style="flex:1;">User</span>
      <span style="width:80px;text-align:right;">Streak</span>
      <span style="width:80px;text-align:right;">Score</span>
    </div>
    """, unsafe_allow_html=True)

    for i, r in enumerate(lb, 1):
        is_me = r["username"] == me
        me_cls = "hf-lb-me" if is_me else ""
        st.markdown(f"""
        <div class="hf-lb-row {me_cls}">
          <span style="font-size:1.05rem;min-width:28px;text-align:center;">
            {medal(i)}</span>
          {avatar(r['display_name'], r['username'], 32)}
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;font-size:0.9rem;color:{S.TEXT};
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              {r['display_name']}
              {'<span style="font-size:0.68rem;color:'+S.ACCENT+';"> · you</span>' if is_me else ''}
            </div>
            <div style="font-size:0.68rem;color:{S.MUTED};">@{r['username']}</div>
          </div>
          <div style="width:80px;text-align:right;">
            <div style="font-weight:700;font-size:0.88rem;color:{S.ACCENT};">
              🔥 {r['best_streak']}d</div>
          </div>
          <div style="width:80px;text-align:right;">
            <div style="font-weight:700;font-size:0.88rem;color:{S.ACCENT3};">
              ⚡ {r['score']:,}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:1rem;font-size:0.72rem;color:{S.MUTED};">
      Score = (Total completions × 10) + (Best streak × 50)
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROFILE
# ─────────────────────────────────────────────────────────────────────────────
def page_profile():
    user_id = uid()
    user    = st.session_state.user
    habits  = db.get_habits(user_id)
    logs    = db.get_logs(user_id)

    st.markdown(f"""
    <div class="hf-page-title">Profile</div>
    <div class="hf-page-sub">Your public page · @{user['username']}</div>
    """, unsafe_allow_html=True)

    # Profile card
    col_av, col_info = st.columns([1, 3])
    with col_av:
        st.markdown(avatar(user["display_name"], user["username"], size=72),
                    unsafe_allow_html=True)
    with col_info:
        score     = db.user_score(user_id)
        best_s    = db.best_streak_across(user_id)
        all_time  = db.total_completions(user_id)
        badge_str = S.get_badge(best_s)
        st.markdown(f"""
        <div style="font-family:'Outfit',sans-serif;">
          <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                      font-weight:700;color:{S.TEXT};">{user['display_name']}</div>
          <div style="font-size:0.8rem;color:{S.MUTED};margin-bottom:8px;">
            @{user['username']} · Member since {user.get('joined','—')}</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <span class="hf-pill hf-pill-gold">⚡ {score:,} pts</span>
            <span class="hf-pill hf-pill-gold">🔥 {best_s}d streak</span>
            {'<span class="hf-pill hf-pill-gold">'+badge_str+'</span>' if badge_str else ''}
            <span class="hf-pill hf-pill-sky">{len(habits)} habits</span>
            <span class="hf-pill hf-pill-green">{all_time} completions</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Achievements
    st.markdown('<div class="hf-section">🏅 Achievements</div>', unsafe_allow_html=True)

    BADGES = {
        "🌱 Sprout":   ("#22c55e", 3,   "3-day streak"),
        "🔥 Ignited":  ("#f97316", 7,   "7-day streak"),
        "⚡ Charged":  (S.ACCENT,  14,  "14-day streak"),
        "💎 Diamond":  (S.ACCENT3, 30,  "30-day streak"),
        "🚀 Elite":    ("#a78bfa", 60,  "60-day streak"),
        "🏆 Legend":   ("#f59e0b", 100, "100-day streak"),
    }
    earned = {S.get_badge(db.streak(user_id, h["id"])) for h in habits} - {""}

    bcols = st.columns(3)
    for i, (badge, (color, threshold, req)) in enumerate(BADGES.items()):
        icon = badge.split()[0]; name = badge.split(" ", 1)[1]
        unlocked = badge in earned
        with bcols[i % 3]:
            if unlocked:
                st.markdown(f"""
                <div style="background:{S.CARD};border:1px solid {color}44;
                            border-radius:14px;padding:1.1rem;text-align:center;
                            box-shadow:0 0 16px {color}22;margin-bottom:0.7rem;">
                  <div style="font-size:1.9rem;">{icon}</div>
                  <div style="font-family:'Playfair Display',serif;font-weight:700;
                              color:{color};font-size:0.88rem;margin:4px 0;">{name}</div>
                  <div style="font-size:0.65rem;color:{S.MUTED};">{req}</div>
                  <div style="margin-top:8px;font-size:0.65rem;background:{color}20;
                              color:{color};border-radius:99px;padding:2px 10px;
                              display:inline-block;font-weight:700;">UNLOCKED</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#0c0c18;border:1px solid #161622;
                            border-radius:14px;padding:1.1rem;text-align:center;
                            opacity:0.38;margin-bottom:0.7rem;">
                  <div style="font-size:1.9rem;filter:grayscale(1);">{icon}</div>
                  <div style="font-family:'Playfair Display',serif;font-weight:700;
                              color:#3a3a5a;font-size:0.88rem;margin:4px 0;">{name}</div>
                  <div style="font-size:0.65rem;color:#2e2e4a;">{req}</div>
                  <div style="margin-top:8px;font-size:0.65rem;background:#161622;
                              color:#3a3a5a;border-radius:99px;padding:2px 10px;
                              display:inline-block;">🔒 locked</div>
                </div>
                """, unsafe_allow_html=True)

    # Manage habits
    st.markdown('<div class="hf-section" style="margin-top:1rem;">⚙️ Manage Habits</div>',
                unsafe_allow_html=True)

    if not habits:
        st.markdown(f"<span style='color:{S.MUTED};font-size:0.84rem;'>No habits yet.</span>",
                    unsafe_allow_html=True)
    else:
        to_del = None
        for h in habits:
            s = db.streak(user_id, h["id"])
            cc, cd = st.columns([6, 1])
            with cc:
                st.markdown(f"""
                <div class="hf-card">
                  <div class="hf-card-bar" style="background:{h.get('color',S.ACCENT)};"></div>
                  <div style="display:flex;align-items:center;gap:9px;padding-left:10px;flex-wrap:wrap;">
                    <span style="font-size:1.2rem;">{h.get('emoji','📌')}</span>
                    <div style="flex:1;">
                      <div style="font-weight:700;font-size:0.9rem;color:{S.TEXT};">{h['name']}</div>
                      <div style="font-size:0.72rem;color:{S.MUTED};">
                        {h.get('category','General')} · {h.get('frequency','Daily')}
                        · Added {h.get('created','—')}</div>
                    </div>
                    <span class="hf-pill hf-pill-gold">🔥 {s}d</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with cd:
                st.markdown('<div class="hf-btn-red">', unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{h['id']}", help="Delete habit"):
                    to_del = h["id"]
                st.markdown('</div>', unsafe_allow_html=True)

        if to_del:
            db.delete_habit(user_id, to_del)
            st.success("Habit deleted.")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear All Logs (keep habits)", type="secondary"):
            db.save_logs_for(user_id, {})
            st.success("All logs cleared.")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.user:
        auth_screen()
        return

    sidebar()

    # Main content with responsive padding
    st.markdown(f"""
    <div style="padding: 0.5rem 0 2rem;">
    """, unsafe_allow_html=True)

    page = st.session_state.page
    if   page == "today":       page_today()
    elif page == "add":         page_add()
    elif page == "analytics":   page_analytics()
    elif page == "challenges":  page_challenges()
    elif page == "leaderboard": page_leaderboard()
    elif page == "profile":     page_profile()
    else:                       page_today()

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
