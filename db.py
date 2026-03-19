"""
db.py  —  Habitforge data layer
All data is stored in JSON files (Streamlit Community Cloud compatible).
For production scale, swap the read/write calls with a real DB (Supabase, etc.)
"""
import json, os, uuid, hashlib
from datetime import date, timedelta

# ── File paths ────────────────────────────────────────────────────────────────
USERS_FILE      = "hf_users.json"
HABITS_FILE     = "hf_habits.json"
LOGS_FILE       = "hf_logs.json"
CHALLENGES_FILE = "hf_challenges.json"
ENROLLMENTS_FILE= "hf_enrollments.json"

# ── Low-level helpers ─────────────────────────────────────────────────────────
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

# ── Users ─────────────────────────────────────────────────────────────────────
def get_users() -> dict:           return _load(USERS_FILE, {})
def save_users(u: dict):           _save(USERS_FILE, u)

def register(username: str, password: str, display_name: str) -> tuple[bool, str]:
    users = get_users()
    key = username.lower().strip()
    if not key or len(key) < 3:
        return False, "Username must be at least 3 characters."
    if not all(c.isalnum() or c in "_-" for c in key):
        return False, "Username: letters, numbers, _ or - only."
    if key in users:
        return False, "Username already taken."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[key] = {
        "id": _uid(),
        "username": key,
        "display_name": display_name.strip() or key,
        "password_hash": _hash(password),
        "joined": today(),
        "avatar_seed": key,          # used for deterministic avatar colour
    }
    save_users(users)
    return True, "Account created!"

def login(username: str, password: str) -> tuple[bool, str, dict | None]:
    users = get_users()
    key = username.lower().strip()
    if key not in users:
        return False, "User not found.", None
    if users[key]["password_hash"] != _hash(password):
        return False, "Incorrect password.", None
    return True, "Welcome back!", users[key]

# ── Habits ────────────────────────────────────────────────────────────────────
def get_habits(user_id: str) -> list:
    all_h = _load(HABITS_FILE, {})
    return all_h.get(user_id, [])

def save_habits(user_id: str, habits: list):
    all_h = _load(HABITS_FILE, {})
    all_h[user_id] = habits
    _save(HABITS_FILE, all_h)

def add_habit(user_id: str, name: str, emoji: str, category: str,
              frequency: str, color: str, note: str, target_days: int) -> dict:
    h = {
        "id": _uid(),
        "name": name.strip(),
        "emoji": emoji.strip() or "📌",
        "category": category,
        "frequency": frequency,
        "color": color,
        "note": note.strip(),
        "target_days": target_days,
        "created": today(),
    }
    habits = get_habits(user_id)
    habits.append(h)
    save_habits(user_id, habits)
    return h

def delete_habit(user_id: str, habit_id: str):
    habits = [h for h in get_habits(user_id) if h["id"] != habit_id]
    save_habits(user_id, habits)

# ── Logs ──────────────────────────────────────────────────────────────────────
def get_logs(user_id: str) -> dict:
    all_l = _load(LOGS_FILE, {})
    return all_l.get(user_id, {})

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

# ── Analytics helpers ─────────────────────────────────────────────────────────
def streak(user_id: str, habit_id: str) -> int:
    logs = get_logs(user_id)
    s, d = 0, date.today()
    while logs.get(f"{habit_id}_{d.isoformat()}", False):
        s += 1; d -= timedelta(days=1)
    return s

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
    """Overall score = total completions × 10 + best streak × 50"""
    return total_completions(user_id) * 10 + best_streak_across(user_id) * 50

# ── Challenges ────────────────────────────────────────────────────────────────
DEFAULT_CHALLENGES = [
    {
        "id": "ch_7day_morning",
        "title": "7-Day Morning Ritual",
        "description": "Complete your morning habit every day for 7 days straight.",
        "emoji": "🌅",
        "duration_days": 7,
        "target_streak": 7,
        "color": "#f59e0b",
        "category": "Consistency",
        "participants": 0,
    },
    {
        "id": "ch_30day_move",
        "title": "30-Day Movement",
        "description": "Log any fitness or movement habit daily for 30 days.",
        "emoji": "🏃",
        "duration_days": 30,
        "target_streak": 30,
        "color": "#22c55e",
        "category": "Fitness",
        "participants": 0,
    },
    {
        "id": "ch_21day_read",
        "title": "21-Day Reader",
        "description": "Read or learn something new every day for 21 days.",
        "emoji": "📚",
        "duration_days": 21,
        "target_streak": 21,
        "color": "#6366f1",
        "category": "Learning",
        "participants": 0,
    },
    {
        "id": "ch_14day_mindful",
        "title": "14-Day Mindfulness",
        "description": "Meditate or journal each day for 2 weeks.",
        "emoji": "🧘",
        "duration_days": 14,
        "target_streak": 14,
        "color": "#8b5cf6",
        "category": "Mental Health",
        "participants": 0,
    },
    {
        "id": "ch_10day_hydrate",
        "title": "10-Day Hydration",
        "description": "Log water/hydration habit 10 days in a row.",
        "emoji": "💧",
        "duration_days": 10,
        "target_streak": 10,
        "color": "#06b6d4",
        "category": "Health",
        "participants": 0,
    },
    {
        "id": "ch_30day_nosocial",
        "title": "Digital Detox Month",
        "description": "Replace 1 hour of social media with intentional activity, daily.",
        "emoji": "📵",
        "duration_days": 30,
        "target_streak": 30,
        "color": "#ec4899",
        "category": "Focus",
        "participants": 0,
    },
]

def get_challenges() -> list:
    stored = _load(CHALLENGES_FILE, None)
    if stored is None:
        _save(CHALLENGES_FILE, DEFAULT_CHALLENGES)
        return DEFAULT_CHALLENGES
    return stored

def get_enrollments(user_id: str) -> list:
    all_e = _load(ENROLLMENTS_FILE, {})
    return all_e.get(user_id, [])

def enroll(user_id: str, challenge_id: str):
    all_e = _load(ENROLLMENTS_FILE, {})
    existing = all_e.get(user_id, [])
    if not any(e["challenge_id"] == challenge_id for e in existing):
        existing.append({
            "challenge_id": challenge_id,
            "joined": today(),
            "completed": False,
        })
        all_e[user_id] = existing
        _save(ENROLLMENTS_FILE, all_e)
        # bump participant count
        challenges = get_challenges()
        for c in challenges:
            if c["id"] == challenge_id:
                c["participants"] = c.get("participants", 0) + 1
        _save(CHALLENGES_FILE, challenges)

def unenroll(user_id: str, challenge_id: str):
    all_e = _load(ENROLLMENTS_FILE, {})
    existing = [e for e in all_e.get(user_id, []) if e["challenge_id"] != challenge_id]
    all_e[user_id] = existing
    _save(ENROLLMENTS_FILE, all_e)

def is_enrolled(user_id: str, challenge_id: str) -> bool:
    return any(e["challenge_id"] == challenge_id for e in get_enrollments(user_id))

# ── Global leaderboard ────────────────────────────────────────────────────────
def global_leaderboard(top_n: int = 20) -> list:
    users = get_users()
    rows  = []
    for uid_key, u in users.items():
        uid = u["id"]
        tc  = total_completions(uid)
        bs  = best_streak_across(uid)
        sc  = user_score(uid)
        rows.append({
            "username":     u["username"],
            "display_name": u["display_name"],
            "score":        sc,
            "total":        tc,
            "best_streak":  bs,
            "joined":       u.get("joined", ""),
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:top_n]

def challenge_leaderboard(challenge_id: str, top_n: int = 10) -> list:
    all_e = _load(ENROLLMENTS_FILE, {})
    users = get_users()
    rows  = []
    for uid_key, u in users.items():
        uid      = u["id"]
        enrolled = all_e.get(uid, [])
        if any(e["challenge_id"] == challenge_id for e in enrolled):
            bs = best_streak_across(uid)
            rows.append({
                "display_name": u["display_name"],
                "username":     u["username"],
                "best_streak":  bs,
                "score":        user_score(uid),
            })
    rows.sort(key=lambda r: r["best_streak"], reverse=True)
    return rows[:top_n]
