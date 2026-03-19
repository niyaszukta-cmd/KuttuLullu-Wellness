# ─── config.py ───────────────────────────────────────────────────────────────
# All constants, colour tokens, data paths, and content for Habitify

PAGE_TITLE = "Habitify — Habit & Discipline Tracker"

# ── File paths ─────────────────────────────────────────────────────────────────
HABITS_FILE = "habits.json"
LOGS_FILE   = "logs.json"

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_DARK      = "#0a0a12"     # deepest background
CARD_BG      = "#111120"     # card / surface
ACCENT       = "#6366f1"     # indigo-500 — primary accent
TEXT_PRIMARY = "#e0e0ff"     # near-white with a blue tint
TEXT_MUTED   = "#6a6a8a"     # de-emphasized text

# ── Achievement badges ─────────────────────────────────────────────────────────
# Maps minimum streak → badge label
BADGE_THRESHOLDS: dict[int, str] = {
    3:   "🌱 Seedling",
    7:   "🔥 On Fire",
    14:  "⚡ Spartan",
    30:  "💎 Diamond",
    60:  "🚀 Elite",
    100: "🏆 Legend",
}

# ── Daily motivational quotes ──────────────────────────────────────────────────
QUOTES: list[str] = [
    "We are what we repeatedly do. Excellence, then, is not an act, but a habit. — Aristotle",
    "Motivation gets you started. Habit keeps you going. — Jim Ryun",
    "Small daily improvements over time lead to stunning results. — Robin Sharma",
    "Discipline is choosing between what you want now and what you want most.",
    "The secret of your future is hidden in your daily routine. — Mike Murdock",
    "You do not rise to the level of your goals. You fall to the level of your systems. — James Clear",
    "Success is the sum of small efforts, repeated day in and day out. — Robert Collier",
    "An ounce of practice is worth more than tons of preaching. — Mahatma Gandhi",
    "Consistency is the hallmark of the unimaginative. But in habit-building, it is genius.",
    "Your daily choices are your autobiography being written in real time.",
    "Chains of habit are too light to be felt until they are too heavy to be broken. — Warren Buffett",
    "The first step toward change is awareness. The second step is acceptance. — Nathaniel Branden",
    "You'll never change your life until you change something you do daily. — John C. Maxwell",
    "All big things come from small beginnings. — James Clear",
    "Don't break the chain. — Jerry Seinfeld",
    "It's not about having time. It's about making time.",
    "Success doesn't come from what you do occasionally. It comes from what you do consistently.",
    "The man who moves a mountain begins by carrying away small stones. — Confucius",
    "Fall in love with the process and the results will come.",
    "A year from now you'll wish you had started today. — Karen Lamb",
    "Habits are the invisible architecture of daily life. — Gretchen Rubin",
    "Do it for who you could be.",
    "Every action you take is a vote for the person you wish to become. — James Clear",
    "Be consistent enough that your future self thanks you.",
    "The quality of your life is determined by the quality of your habits.",
    "Hard choices, easy life. Easy choices, hard life. — Jerzy Gregorek",
    "Don't count the days. Make the days count. — Muhammad Ali",
    "The successful warrior is the average man with laser-like focus. — Bruce Lee",
    "With self-discipline, almost anything is possible. — Theodore Roosevelt",
    "What you do every day matters more than what you do every once in a while.",
]
