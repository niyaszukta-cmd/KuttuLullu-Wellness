"""
db.py  —  Habitforge data layer

Challenge flow:
  1. User joins a challenge  → enroll() creates a dedicated "challenge habit"
                                 in the user's habit list (tagged with challenge_id)
  2. User logs it in Today   → normal toggle_log() against that habit_id
  3. Leaderboard             → ranked by streak on that specific challenge habit

This means challenge progress integrates seamlessly with the existing
habit/log/streak infrastructure — no separate tracking layer needed.
"""
import json, os, uuid, hashlib
from datetime import date, timedelta

# ── File paths ─────────────────────────────────────────────────────────────────
USERS_FILE       = "hf_users.json"
HABITS_FILE      = "hf_habits.json"
LOGS_FILE        = "hf_logs.json"
CHALLENGES_FILE  = "hf_challenges.json"
ENROLLMENTS_FILE = "hf_enrollments.json"

# ── Low-level helpers ──────────────────────────────────────────────────────────
def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except Exception: return default
    return default

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _uid() -> str:
    return str(uuid.uuid4())[:10]

def today() -> str:
    return date.today().isoformat()

# ── Users ──────────────────────────────────────────────────────────────────────
def get_users() -> dict:      return _load(USERS_FILE, {})
def save_users(u: dict):      _save(USERS_FILE, u)

def register(username: str, password: str, display_name: str) -> tuple:
    users = get_users()
    key   = username.lower().strip()
    if not key or len(key) < 3:
        return False, "Username must be at least 3 characters."
    if not all(c.isalnum() or c in "_-" for c in key):
        return False, "Username: letters, numbers, _ or - only."
    if key in users:
        return False, "Username already taken."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[key] = {
        "id":            _uid(),
        "username":      key,
        "display_name":  display_name.strip() or key,
        "password_hash": _hash(password),
        "joined":        today(),
        "avatar_seed":   key,
    }
    save_users(users)
    return True, "Account created!"

def login(username: str, password: str) -> tuple:
    users = get_users()
    key   = username.lower().strip()
    if key not in users:
        return False, "User not found.", None
    if users[key]["password_hash"] != _hash(password):
        return False, "Incorrect password.", None
    return True, "Welcome back!", users[key]

# ── Habits ─────────────────────────────────────────────────────────────────────
def get_habits(user_id: str) -> list:
    return _load(HABITS_FILE, {}).get(user_id, [])

def save_habits(user_id: str, habits: list):
    all_h = _load(HABITS_FILE, {})
    all_h[user_id] = habits
    _save(HABITS_FILE, all_h)

def add_habit(user_id: str, name: str, emoji: str, category: str,
              frequency: str, color: str, note: str, target_days: int,
              challenge_id: str = None) -> dict:
    """Add a habit. If challenge_id is set, this habit is a challenge tracker."""
    h = {
        "id":           _uid(),
        "name":         name.strip(),
        "emoji":        emoji.strip() or "📌",
        "category":     category,
        "frequency":    frequency,
        "color":        color,
        "note":         note.strip(),
        "target_days":  target_days,
        "created":      today(),
        "challenge_id": challenge_id,   # None for regular habits
    }
    habits = get_habits(user_id)
    habits.append(h)
    save_habits(user_id, habits)
    return h

def delete_habit(user_id: str, habit_id: str):
    habits = [h for h in get_habits(user_id) if h["id"] != habit_id]
    save_habits(user_id, habits)

def get_challenge_habit(user_id: str, challenge_id: str) -> dict | None:
    """Return the habit that was auto-created when user joined a challenge."""
    return next(
        (h for h in get_habits(user_id) if h.get("challenge_id") == challenge_id),
        None
    )

# ── Logs ───────────────────────────────────────────────────────────────────────
def get_logs(user_id: str) -> dict:
    return _load(LOGS_FILE, {}).get(user_id, {})

def save_logs_for(user_id: str, logs: dict):
    all_l = _load(LOGS_FILE, {})
    all_l[user_id] = logs
    _save(LOGS_FILE, all_l)

def toggle_log(user_id: str, habit_id: str) -> bool:
    logs = get_logs(user_id)
    key  = f"{habit_id}_{today()}"
    logs[key] = not logs.get(key, False)
    save_logs_for(user_id, logs)
    return logs[key]

def is_done_today(user_id: str, habit_id: str) -> bool:
    return get_logs(user_id).get(f"{habit_id}_{today()}", False)

def log_challenge_today(user_id: str, challenge_id: str) -> bool:
    """Toggle today's log for a challenge habit. Returns new state."""
    h = get_challenge_habit(user_id, challenge_id)
    if h:
        return toggle_log(user_id, h["id"])
    return False

def is_challenge_done_today(user_id: str, challenge_id: str) -> bool:
    h = get_challenge_habit(user_id, challenge_id)
    return is_done_today(user_id, h["id"]) if h else False

# ── Analytics helpers ──────────────────────────────────────────────────────────
def streak(user_id: str, habit_id: str) -> int:
    logs = get_logs(user_id)
    s, d = 0, date.today()
    while logs.get(f"{habit_id}_{d.isoformat()}", False):
        s += 1; d -= timedelta(days=1)
    return s

def challenge_streak(user_id: str, challenge_id: str) -> int:
    h = get_challenge_habit(user_id, challenge_id)
    return streak(user_id, h["id"]) if h else 0

def challenge_progress(user_id: str, challenge_id: str) -> dict:
    """Returns days_done, streak, pct, days_since_joined."""
    enrs = get_enrollments(user_id)
    enr  = next((e for e in enrs if e["challenge_id"] == challenge_id), None)
    if not enr:
        return {"days_done": 0, "streak": 0, "pct": 0, "days_active": 0, "target": 0}

    challenge = next((c for c in get_challenges() if c["id"] == challenge_id), {})
    target    = challenge.get("target_streak", 30)
    joined    = date.fromisoformat(enr["joined"])
    days_active = (date.today() - joined).days + 1

    h = get_challenge_habit(user_id, challenge_id)
    if not h:
        return {"days_done": 0, "streak": 0, "pct": 0, "days_active": days_active, "target": target}

    logs     = get_logs(user_id)
    days_done = sum(
        1 for i in range(days_active)
        if logs.get(f"{h['id']}_{(date.today()-timedelta(days=i)).isoformat()}", False)
    )
    s   = streak(user_id, h["id"])
    pct = min(s / target * 100, 100) if target else 0
    return {
        "days_done":   days_done,
        "streak":      s,
        "pct":         pct,
        "days_active": days_active,
        "target":      target,
        "habit_id":    h["id"],
    }

def completion_rate(user_id: str, habit_id: str, days: int = 30) -> float:
    logs = get_logs(user_id)
    done = sum(1 for i in range(days)
               if logs.get(f"{habit_id}_{(date.today()-timedelta(days=i)).isoformat()}", False))
    return done / days * 100

def total_completions(user_id: str) -> int:
    return sum(1 for v in get_logs(user_id).values() if v)

def best_streak_across(user_id: str) -> int:
    habits = get_habits(user_id)
    return max((streak(user_id, h["id"]) for h in habits), default=0)

def user_score(user_id: str) -> int:
    return total_completions(user_id) * 10 + best_streak_across(user_id) * 50

# ── Challenges ─────────────────────────────────────────────────────────────────
DEFAULT_CHALLENGES = [
    {
        "id": "ch_7day_morning", "title": "7-Day Morning Ritual",
        "description": "Complete your morning habit every day for 7 days straight.",
        "emoji": "🌅", "duration_days": 7, "target_streak": 7,
        "color": "#f59e0b", "category": "Consistency", "participants": 0,
        "habit_name": "Morning Ritual", "habit_emoji": "🌅",
        "habit_note": "Part of the 7-Day Morning Ritual challenge.",
    },
    {
        "id": "ch_30day_move", "title": "30-Day Movement",
        "description": "Log any fitness or movement habit daily for 30 days.",
        "emoji": "🏃", "duration_days": 30, "target_streak": 30,
        "color": "#22c55e", "category": "Fitness", "participants": 0,
        "habit_name": "Daily Movement", "habit_emoji": "🏃",
        "habit_note": "Part of the 30-Day Movement challenge.",
    },
    {
        "id": "ch_21day_read", "title": "21-Day Reader",
        "description": "Read or learn something new every day for 21 days.",
        "emoji": "📚", "duration_days": 21, "target_streak": 21,
        "color": "#6366f1", "category": "Learning", "participants": 0,
        "habit_name": "Daily Reading", "habit_emoji": "📚",
        "habit_note": "Part of the 21-Day Reader challenge.",
    },
    {
        "id": "ch_14day_mindful", "title": "14-Day Mindfulness",
        "description": "Meditate or journal each day for 2 weeks.",
        "emoji": "🧘", "duration_days": 14, "target_streak": 14,
        "color": "#8b5cf6", "category": "Mental Health", "participants": 0,
        "habit_name": "Mindfulness Practice", "habit_emoji": "🧘",
        "habit_note": "Part of the 14-Day Mindfulness challenge.",
    },
    {
        "id": "ch_10day_hydrate", "title": "10-Day Hydration",
        "description": "Log water/hydration habit 10 days in a row.",
        "emoji": "💧", "duration_days": 10, "target_streak": 10,
        "color": "#06b6d4", "category": "Health", "participants": 0,
        "habit_name": "Daily Hydration", "habit_emoji": "💧",
        "habit_note": "Part of the 10-Day Hydration challenge.",
    },
    {
        "id": "ch_30day_nosocial", "title": "Digital Detox Month",
        "description": "Replace 1 hour of social media with intentional activity, daily.",
        "emoji": "📵", "duration_days": 30, "target_streak": 30,
        "color": "#ec4899", "category": "Focus", "participants": 0,
        "habit_name": "Digital Detox", "habit_emoji": "📵",
        "habit_note": "Part of the Digital Detox Month challenge.",
    },
]

def get_challenges() -> list:
    stored = _load(CHALLENGES_FILE, None)
    if stored is None:
        _save(CHALLENGES_FILE, DEFAULT_CHALLENGES)
        return DEFAULT_CHALLENGES
    return stored

def get_enrollments(user_id: str) -> list:
    return _load(ENROLLMENTS_FILE, {}).get(user_id, [])

def enroll(user_id: str, challenge_id: str):
    """
    Join a challenge:
    1. Record enrollment
    2. Auto-create a dedicated habit for this challenge
    3. Bump participant count
    """
    all_e    = _load(ENROLLMENTS_FILE, {})
    existing = all_e.get(user_id, [])
    if any(e["challenge_id"] == challenge_id for e in existing):
        return  # already enrolled

    # Find challenge definition
    challenge = next((c for c in get_challenges() if c["id"] == challenge_id), None)
    if not challenge:
        return

    # Record enrollment
    existing.append({
        "challenge_id": challenge_id,
        "joined":       today(),
        "completed":    False,
    })
    all_e[user_id] = existing
    _save(ENROLLMENTS_FILE, all_e)

    # Auto-create the challenge habit (tagged with challenge_id)
    add_habit(
        user_id      = user_id,
        name         = challenge.get("habit_name", challenge["title"]),
        emoji        = challenge.get("habit_emoji", challenge["emoji"]),
        category     = challenge.get("category", "General"),
        frequency    = "Daily",
        color        = challenge["color"],
        note         = challenge.get("habit_note", f'Challenge: {challenge["title"]}'),
        target_days  = 7,
        challenge_id = challenge_id,
    )

    # Bump participant count
    challenges = get_challenges()
    for c in challenges:
        if c["id"] == challenge_id:
            c["participants"] = c.get("participants", 0) + 1
    _save(CHALLENGES_FILE, challenges)

def unenroll(user_id: str, challenge_id: str):
    """Leave a challenge and remove its auto-created habit."""
    all_e    = _load(ENROLLMENTS_FILE, {})
    existing = [e for e in all_e.get(user_id, []) if e["challenge_id"] != challenge_id]
    all_e[user_id] = existing
    _save(ENROLLMENTS_FILE, all_e)

    # Remove the challenge habit
    habits = [h for h in get_habits(user_id) if h.get("challenge_id") != challenge_id]
    save_habits(user_id, habits)

    # Decrement participant count
    challenges = get_challenges()
    for c in challenges:
        if c["id"] == challenge_id:
            c["participants"] = max(0, c.get("participants", 1) - 1)
    _save(CHALLENGES_FILE, challenges)

def is_enrolled(user_id: str, challenge_id: str) -> bool:
    return any(e["challenge_id"] == challenge_id for e in get_enrollments(user_id))

# ── Global leaderboard ─────────────────────────────────────────────────────────
def global_leaderboard(top_n: int = 20) -> list:
    users = get_users()
    rows  = []
    for _, u in users.items():
        uid = u["id"]
        rows.append({
            "username":     u["username"],
            "display_name": u["display_name"],
            "score":        user_score(uid),
            "total":        total_completions(uid),
            "best_streak":  best_streak_across(uid),
            "joined":       u.get("joined", ""),
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:top_n]

def challenge_leaderboard(challenge_id: str, top_n: int = 10) -> list:
    """Ranked by streak on the challenge-specific habit."""
    all_e = _load(ENROLLMENTS_FILE, {})
    users = get_users()
    rows  = []
    for _, u in users.items():
        uid      = u["id"]
        enrolled = all_e.get(uid, [])
        if not any(e["challenge_id"] == challenge_id for e in enrolled):
            continue
        prog = challenge_progress(uid, challenge_id)
        rows.append({
            "display_name": u["display_name"],
            "username":     u["username"],
            "streak":       prog["streak"],
            "days_done":    prog["days_done"],
            "pct":          prog["pct"],
            "score":        user_score(uid),
        })
    rows.sort(key=lambda r: (r["streak"], r["days_done"]), reverse=True)
    return rows[:top_n]
