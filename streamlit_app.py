from __future__ import annotations

import sqlite3
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

APP_NAME = "FocusFlow"
APP_TAGLINE = "A smart study planner that turns deadlines into a realistic plan."
DATABASE_PATH = Path("focusflow.db")

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

PRIORITY_WEIGHT = {
    "Low": 1,
    "Medium": 3,
    "High": 5,
    "Critical": 7,
}

TASK_ICONS = {
    "Homework": "📝",
    "Exam": "🧠",
    "Quiz": "❓",
    "Project": "💻",
    "Reading": "📖",
    "Presentation": "🎤",
    "Other": "📌",
}

SUBJECT_COLORS = [
    "#2563EB", "#7C3AED", "#DB2777", "#EA580C",
    "#059669", "#0891B2", "#4F46E5", "#B45309",
]


st.set_page_config(
    page_title=f"{APP_NAME} | Smart Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL STYLING
# =========================================================

st.markdown(
    """
    <style>
        :root {
            --primary: #4F46E5;
            --primary-dark: #3730A3;
            --surface: #FFFFFF;
            --muted: #64748B;
            --border: rgba(100, 116, 139, 0.20);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(79,70,229,0.08), transparent 28rem),
                radial-gradient(circle at top right, rgba(14,165,233,0.07), transparent 24rem);
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.35rem;
            padding-bottom: 3.5rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
        }

        .brand-card {
            padding: 1rem 1.05rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #4F46E5, #2563EB);
            color: white;
            box-shadow: 0 12px 30px rgba(79,70,229,0.22);
            margin-bottom: 1rem;
        }

        .brand-name {
            font-size: 1.45rem;
            font-weight: 800;
            margin: 0;
        }

        .brand-caption {
            opacity: 0.86;
            font-size: 0.82rem;
            margin-top: 0.25rem;
        }

        .hero {
            padding: 1.35rem 1.5rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: rgba(255,255,255,0.72);
            backdrop-filter: blur(8px);
            margin-bottom: 1.25rem;
        }

        .hero h1 {
            font-size: 2.3rem;
            line-height: 1.1;
            margin: 0;
            letter-spacing: -0.04em;
        }

        .hero p {
            color: var(--muted);
            font-size: 1rem;
            margin: 0.55rem 0 0;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 760;
            margin: 0.2rem 0 0.85rem;
        }

        .task-card {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(255,255,255,0.82);
            padding: 0.95rem 1rem;
            margin-bottom: 0.65rem;
            box-shadow: 0 4px 14px rgba(15,23,42,0.035);
        }

        .task-card:hover {
            transform: translateY(-1px);
            transition: 0.15s ease;
            box-shadow: 0 8px 20px rgba(15,23,42,0.07);
        }

        .status-overdue { border-left: 6px solid #B91C1C; }
        .status-urgent { border-left: 6px solid #EF4444; }
        .status-soon { border-left: 6px solid #F59E0B; }
        .status-track { border-left: 6px solid #10B981; }

        .badge {
            display: inline-block;
            padding: 0.22rem 0.52rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-right: 0.25rem;
        }

        .badge-red { background: #FEE2E2; color: #991B1B; }
        .badge-orange { background: #FEF3C7; color: #92400E; }
        .badge-green { background: #D1FAE5; color: #065F46; }
        .badge-blue { background: #DBEAFE; color: #1E40AF; }
        .badge-purple { background: #EDE9FE; color: #5B21B6; }
        .badge-gray { background: #E2E8F0; color: #334155; }

        .muted {
            color: var(--muted);
            font-size: 0.88rem;
        }

        .recommendation {
            padding: 1.1rem 1.15rem;
            border-radius: 18px;
            color: white;
            background: linear-gradient(135deg, #4338CA, #2563EB);
            box-shadow: 0 14px 34px rgba(37,99,235,0.18);
        }

        .recommendation .small {
            opacity: 0.86;
            font-size: 0.85rem;
        }

        .day-card {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(255,255,255,0.78);
            padding: 0.9rem;
            margin-bottom: 0.7rem;
        }

        .session-row {
            padding: 0.65rem 0.72rem;
            border-radius: 12px;
            background: rgba(241,245,249,0.80);
            margin-top: 0.45rem;
            border: 1px solid rgba(148,163,184,0.18);
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.76);
            border: 1px solid var(--border);
            padding: 0.85rem 0.95rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(15,23,42,0.03);
        }

        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 11px;
            font-weight: 650;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        .stTextArea textarea {
            border-radius: 10px;
        }

        div[data-baseweb="select"] > div {
            border-radius: 10px;
        }

        @media (max-width: 800px) {
            .hero h1 { font-size: 1.8rem; }
            .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE LAYER
# =========================================================

def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                task_type TEXT NOT NULL,
                due_date TEXT NOT NULL,
                due_time TEXT NOT NULL,
                estimated_hours REAL NOT NULL,
                completed_hours REAL NOT NULL DEFAULT 0,
                priority TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                preferred_session_minutes INTEGER NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS availability (
                day_name TEXT PRIMARY KEY,
                available_hours REAL NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
            """
        )

        # Upgrade older databases that may not have start/end time columns.
        availability_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(availability)").fetchall()
        }

        if "start_time" not in availability_columns:
            connection.execute(
                "ALTER TABLE availability ADD COLUMN start_time TEXT NOT NULL DEFAULT '16:00'"
            )
        if "end_time" not in availability_columns:
            connection.execute(
                "ALTER TABLE availability ADD COLUMN end_time TEXT NOT NULL DEFAULT '21:00'"
            )

        for day_name in WEEKDAYS:
            default_hours = 3.0 if day_name not in {"Saturday", "Sunday"} else 4.0
            default_start = "16:00" if day_name not in {"Saturday", "Sunday"} else "10:00"
            default_end = "21:00" if day_name not in {"Saturday", "Sunday"} else "18:00"

            connection.execute(
                """
                INSERT OR IGNORE INTO availability
                    (day_name, available_hours, start_time, end_time)
                VALUES (?, ?, ?, ?)
                """,
                (day_name, default_hours, default_start, default_end),
            )

        defaults = {
            "plan_days": "7",
            "break_minutes": "10",
            "weekend_enabled": "true",
        }

        for key, value in defaults.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO settings (setting_key, setting_value)
                VALUES (?, ?)
                """,
                (key, value),
            )


def create_task(
    subject: str,
    title: str,
    task_type: str,
    due_date: date,
    due_time: time,
    estimated_hours: float,
    priority: str,
    difficulty: int,
    preferred_session_minutes: int,
    notes: str,
) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO tasks (
                subject, title, task_type, due_date, due_time,
                estimated_hours, completed_hours, priority,
                difficulty, preferred_session_minutes, notes,
                completed, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 0, ?)
            """,
            (
                subject.strip(),
                title.strip(),
                task_type,
                due_date.isoformat(),
                due_time.strftime("%H:%M"),
                float(estimated_hours),
                priority,
                int(difficulty),
                int(preferred_session_minutes),
                notes.strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def read_tasks(include_completed: bool = True) -> list[dict]:
    query = "SELECT * FROM tasks"
    if not include_completed:
        query += " WHERE completed = 0"
    query += " ORDER BY completed ASC, due_date ASC, due_time ASC"

    with connect() as connection:
        rows = connection.execute(query).fetchall()

    return [dict(row) for row in rows]


def read_task(task_id: int) -> dict | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return dict(row) if row else None


def update_task_progress(task_id: int, completed_hours: float) -> None:
    task = read_task(task_id)
    if task is None:
        return

    safe_hours = max(
        0.0,
        min(float(completed_hours), float(task["estimated_hours"])),
    )
    is_complete = int(safe_hours >= float(task["estimated_hours"]))

    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed_hours = ?, completed = ?
            WHERE id = ?
            """,
            (safe_hours, is_complete, task_id),
        )


def update_task_details(
    task_id: int,
    subject: str,
    title: str,
    due_date_value: date,
    due_time_value: time,
    priority: str,
    estimated_hours: float,
) -> None:
    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET subject = ?,
                title = ?,
                due_date = ?,
                due_time = ?,
                priority = ?,
                estimated_hours = ?,
                completed_hours = MIN(completed_hours, ?)
            WHERE id = ?
            """,
            (
                subject.strip(),
                title.strip(),
                due_date_value.isoformat(),
                due_time_value.strftime("%H:%M"),
                priority,
                float(estimated_hours),
                float(estimated_hours),
                task_id,
            ),
        )


def set_task_completed(task_id: int, completed: bool) -> None:
    task = read_task(task_id)
    if task is None:
        return

    completed_hours = (
        float(task["estimated_hours"])
        if completed
        else min(float(task["completed_hours"]), float(task["estimated_hours"]) - 0.5)
    )
    completed_hours = max(0.0, completed_hours)

    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed = ?, completed_hours = ?
            WHERE id = ?
            """,
            (int(completed), completed_hours, task_id),
        )


def remove_task(task_id: int) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def read_availability() -> dict[str, dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT day_name, available_hours, start_time, end_time
            FROM availability
            """
        ).fetchall()

    result = {
        row["day_name"]: {
            "hours": float(row["available_hours"]),
            "start": row["start_time"],
            "end": row["end_time"],
        }
        for row in rows
    }

    return {
        day: result.get(
            day,
            {"hours": 0.0, "start": "16:00", "end": "21:00"},
        )
        for day in WEEKDAYS
    }


def save_availability(values: dict[str, dict]) -> None:
    with connect() as connection:
        for day_name, data in values.items():
            connection.execute(
                """
                INSERT INTO availability
                    (day_name, available_hours, start_time, end_time)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(day_name)
                DO UPDATE SET
                    available_hours = excluded.available_hours,
                    start_time = excluded.start_time,
                    end_time = excluded.end_time
                """,
                (
                    day_name,
                    float(data["hours"]),
                    data["start"],
                    data["end"],
                ),
            )


def get_setting(key: str, fallback: str) -> str:
    with connect() as connection:
        row = connection.execute(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,),
        ).fetchone()

    return str(row["setting_value"]) if row else fallback


def set_setting(key: str, value: str) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO settings (setting_key, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_key)
            DO UPDATE SET setting_value = excluded.setting_value
            """,
            (key, str(value)),
        )


# =========================================================
# SMART LOGIC
# =========================================================

def deadline_datetime(task: dict) -> datetime:
    due_date_value = date.fromisoformat(task["due_date"])
    due_time_value = time.fromisoformat(task["due_time"])
    return datetime.combine(due_date_value, due_time_value)


def task_hours_left(task: dict) -> float:
    return max(
        0.0,
        float(task["estimated_hours"]) - float(task["completed_hours"]),
    )


def days_left(task: dict) -> float:
    return (
        deadline_datetime(task) - datetime.now()
    ).total_seconds() / 86400


def urgency_info(task: dict) -> dict:
    remaining_days = days_left(task)

    if remaining_days < 0:
        return {
            "label": "Overdue",
            "icon": "⛔",
            "css": "status-overdue",
            "badge": "badge-red",
        }

    if remaining_days <= 1:
        return {
            "label": "Urgent",
            "icon": "🔴",
            "css": "status-urgent",
            "badge": "badge-red",
        }

    if remaining_days <= 3:
        return {
            "label": "Due soon",
            "icon": "🟠",
            "css": "status-soon",
            "badge": "badge-orange",
        }

    return {
        "label": "On track",
        "icon": "🟢",
        "css": "status-track",
        "badge": "badge-green",
    }


def calculate_smart_score(task: dict) -> float:
    """
    Scores tasks using deadline urgency, priority, difficulty,
    remaining workload, and the amount of time left.
    """

    remaining_days = days_left(task)
    remaining_hours = task_hours_left(task)

    if remaining_days < 0:
        deadline_score = 36
    else:
        deadline_score = 22 / (remaining_days + 0.75)

    priority_score = PRIORITY_WEIGHT.get(task["priority"], 3) * 3.25
    difficulty_score = int(task["difficulty"]) * 1.35
    pressure_score = remaining_hours / max(remaining_days, 0.5) * 3

    return round(
        deadline_score + priority_score + difficulty_score + pressure_score,
        2,
    )


def recommendation_reason(task: dict) -> str:
    reasons: list[str] = []
    remaining_days = days_left(task)

    if remaining_days < 0:
        reasons.append("it is overdue")
    elif remaining_days <= 1:
        reasons.append("the deadline is within 24 hours")
    elif remaining_days <= 3:
        reasons.append("the deadline is approaching")

    if task["priority"] in {"High", "Critical"}:
        reasons.append(f"it has {task['priority'].lower()} priority")

    if int(task["difficulty"]) >= 4:
        reasons.append("it is difficult")

    if task_hours_left(task) >= 5:
        reasons.append("it has a large remaining workload")

    if not reasons:
        reasons.append("starting early will prevent last-minute work")

    return "; ".join(reasons).capitalize()


def next_rounded_time(current: datetime) -> datetime:
    if current.minute == 0:
        return current.replace(second=0, microsecond=0)

    rounded_hour = current.replace(minute=0, second=0, microsecond=0)
    return rounded_hour + timedelta(hours=1)


def build_smart_timetable(
    tasks: list[dict],
    availability: dict[str, dict],
    plan_days: int,
    break_minutes: int,
) -> tuple[list[dict], list[str]]:
    today = date.today()
    final_date = today + timedelta(days=plan_days - 1)
    now = datetime.now()

    active_tasks = [
        task.copy()
        for task in tasks
        if not bool(task["completed"]) and task_hours_left(task) > 0
    ]

    for task in active_tasks:
        task["_minutes_left"] = int(round(task_hours_left(task) * 60))
        task["_score"] = calculate_smart_score(task)

    active_tasks.sort(
        key=lambda task: (-task["_score"], deadline_datetime(task))
    )

    dates: list[date] = []
    current_date = today
    while current_date <= final_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    capacity: dict[date, int] = {}
    next_time: dict[date, datetime] = {}
    hard_end: dict[date, datetime] = {}

    for day_date in dates:
        weekday = day_date.strftime("%A")
        day_settings = availability[weekday]

        start_clock = time.fromisoformat(day_settings["start"])
        end_clock = time.fromisoformat(day_settings["end"])

        start_dt = datetime.combine(day_date, start_clock)
        end_dt = datetime.combine(day_date, end_clock)

        if day_date == today:
            start_dt = max(start_dt, next_rounded_time(now))

        window_minutes = max(
            0,
            int((end_dt - start_dt).total_seconds() // 60),
        )
        declared_minutes = int(round(day_settings["hours"] * 60))

        capacity[day_date] = min(window_minutes, declared_minutes)
        next_time[day_date] = start_dt
        hard_end[day_date] = end_dt

    schedule: list[dict] = []
    warnings: list[str] = []

    for task in active_tasks:
        due_dt = deadline_datetime(task)
        preferred = max(
            25,
            min(int(task["preferred_session_minutes"]), 120),
        )

        if due_dt.date() < today:
            eligible_dates = dates
        else:
            eligible_dates = [
                day_date
                for day_date in dates
                if day_date <= due_dt.date()
            ]

        while task["_minutes_left"] > 0:
            possible_dates = [
                day_date
                for day_date in eligible_dates
                if capacity[day_date] >= 25
            ]

            if not possible_dates:
                break

            # Balance urgency with workload distribution:
            # prefer earlier days, then days with more remaining capacity.
            chosen_date = min(
                possible_dates,
                key=lambda day_date: (
                    (day_date - today).days,
                    -capacity[day_date],
                ),
            )

            session_minutes = min(
                preferred,
                task["_minutes_left"],
                capacity[chosen_date],
            )

            if session_minutes < 25 and task["_minutes_left"] >= 25:
                capacity[chosen_date] = 0
                continue

            start_dt = next_time[chosen_date]
            end_dt = start_dt + timedelta(minutes=session_minutes)

            if end_dt > hard_end[chosen_date]:
                capacity[chosen_date] = 0
                continue

            urgency = urgency_info(task)

            schedule.append(
                {
                    "Date": chosen_date,
                    "Day": chosen_date.strftime("%A"),
                    "Start": start_dt.strftime("%I:%M %p").lstrip("0"),
                    "End": end_dt.strftime("%I:%M %p").lstrip("0"),
                    "Subject": task["subject"],
                    "Task": task["title"],
                    "Type": task["task_type"],
                    "Minutes": session_minutes,
                    "Study Time": f"{session_minutes / 60:.1f} hr",
                    "Priority": task["priority"],
                    "Urgency": urgency["label"],
                    "Reason": recommendation_reason(task),
                    "Task ID": task["id"],
                    "Smart Score": task["_score"],
                }
            )

            task["_minutes_left"] -= session_minutes
            capacity[chosen_date] -= session_minutes

            break_end = end_dt + timedelta(minutes=break_minutes)
            next_time[chosen_date] = min(break_end, hard_end[chosen_date])

            # Breaks consume part of the real time window but not declared study hours.
            if next_time[chosen_date] >= hard_end[chosen_date]:
                capacity[chosen_date] = 0

        if task["_minutes_left"] > 0:
            warnings.append(
                f"{task['subject']} — {task['title']} still needs "
                f"{task['_minutes_left'] / 60:.1f} unscheduled hour(s)."
            )

    schedule.sort(
        key=lambda session: (
            session["Date"],
            datetime.strptime(session["Start"], "%I:%M %p").time(),
        )
    )

    return schedule, warnings


def task_table(tasks: list[dict]) -> pd.DataFrame:
    rows = []

    for task in tasks:
        urgency = urgency_info(task)
        estimated = float(task["estimated_hours"])
        completed = float(task["completed_hours"])
        progress = completed / estimated if estimated else 0

        rows.append(
            {
                "ID": task["id"],
                "Status": "Completed" if task["completed"] else urgency["label"],
                "Subject": task["subject"],
                "Task": task["title"],
                "Type": task["task_type"],
                "Deadline": deadline_datetime(task).strftime(
                    "%b %d, %Y · %I:%M %p"
                ),
                "Priority": task["priority"],
                "Difficulty": f"{task['difficulty']}/5",
                "Hours Left": round(task_hours_left(task), 1),
                "Progress": f"{progress * 100:.0f}%",
                "Smart Score": calculate_smart_score(task),
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# SHARED UI COMPONENTS
# =========================================================

def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>Plan smarter. Study with purpose.</h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task: dict) -> None:
    urgency = urgency_info(task)
    deadline = deadline_datetime(task).strftime("%a, %b %d at %I:%M %p")
    task_icon = TASK_ICONS.get(task["task_type"], "📌")

    priority_badge = (
        "badge-red"
        if task["priority"] == "Critical"
        else "badge-orange"
        if task["priority"] == "High"
        else "badge-blue"
    )

    st.markdown(
        f"""
        <div class="task-card {urgency['css']}">
            <div style="font-size:1.02rem;font-weight:760;">
                {task_icon} {task["subject"]}: {task["title"]}
            </div>
            <div style="margin-top:0.45rem;">
                <span class="badge {urgency['badge']}">
                    {urgency['icon']} {urgency['label']}
                </span>
                <span class="badge {priority_badge}">
                    {task["priority"]} priority
                </span>
                <span class="badge badge-gray">
                    {task_hours_left(task):.1f} hours left
                </span>
            </div>
            <div class="muted" style="margin-top:0.55rem;">
                Due {deadline} · Difficulty {task["difficulty"]}/5
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PAGES
# =========================================================

def dashboard_page(tasks: list[dict], availability: dict[str, dict]) -> None:
    active = [task for task in tasks if not task["completed"]]
    completed = [task for task in tasks if task["completed"]]

    urgent_or_overdue = [
        task for task in active if days_left(task) <= 1
    ]
    total_hours_left = sum(task_hours_left(task) for task in active)
    weekly_capacity = sum(day["hours"] for day in availability.values())

    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active tasks", len(active))
    c2.metric("Hours remaining", f"{total_hours_left:.1f}")
    c3.metric("Urgent / overdue", len(urgent_or_overdue))
    c4.metric("Weekly capacity", f"{weekly_capacity:.1f} hr")

    if tasks:
        completion_rate = len(completed) / len(tasks)
        st.caption("Overall completion")
        st.progress(completion_rate)
        st.caption(
            f"{len(completed)} of {len(tasks)} tasks completed "
            f"({completion_rate * 100:.0f}%)"
        )

    if urgent_or_overdue:
        overdue_count = sum(1 for task in urgent_or_overdue if days_left(task) < 0)
        if overdue_count:
            st.error(
                f"{overdue_count} task(s) are overdue. "
                "Open the Smart Timetable to schedule recovery sessions."
            )
        else:
            st.warning(
                f"{len(urgent_or_overdue)} task(s) are due within 24 hours."
            )
    elif active:
        st.success("You are currently clear of urgent and overdue work.")

    st.divider()

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown(
            '<div class="section-title">Best next action</div>',
            unsafe_allow_html=True,
        )

        if not active:
            st.info("Add a task to receive a smart recommendation.")
        else:
            best_task = max(active, key=calculate_smart_score)
            icon = TASK_ICONS.get(best_task["task_type"], "📌")

            st.markdown(
                f"""
                <div class="recommendation">
                    <div class="small">RECOMMENDED NEXT</div>
                    <div style="font-size:1.35rem;font-weight:800;margin-top:0.3rem;">
                        {icon} {best_task["subject"]}: {best_task["title"]}
                    </div>
                    <div style="margin-top:0.55rem;">
                        {recommendation_reason(best_task)}.
                    </div>
                    <div class="small" style="margin-top:0.7rem;">
                        Smart score {calculate_smart_score(best_task)} ·
                        {task_hours_left(best_task):.1f} hours remaining
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            '<div class="section-title">Workload by subject</div>',
            unsafe_allow_html=True,
        )

        if not active:
            st.info("No active workload to display.")
        else:
            workload: dict[str, float] = {}
            for task in active:
                workload[task["subject"]] = (
                    workload.get(task["subject"], 0.0)
                    + task_hours_left(task)
                )

            chart_data = (
                pd.DataFrame(
                    {
                        "Subject": list(workload.keys()),
                        "Hours": list(workload.values()),
                    }
                )
                .sort_values("Hours", ascending=False)
                .set_index("Subject")
            )
            st.bar_chart(chart_data)

    st.divider()
    st.markdown(
        '<div class="section-title">Upcoming deadlines</div>',
        unsafe_allow_html=True,
    )

    if not active:
        st.info("No active deadlines.")
    else:
        for task in sorted(active, key=deadline_datetime)[:7]:
            render_task_card(task)


def add_task_page() -> None:
    st.markdown(
        '<div class="section-title">Create a study task</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "The more accurate your deadline and estimated hours are, "
        "the more realistic the timetable will be."
    )

    with st.form("new_task_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
            subject = st.text_input(
                "Subject *",
                placeholder="Example: Mathematics",
            )
            title = st.text_input(
                "Task name *",
                placeholder="Example: Prepare for Chapter 5 exam",
            )
            task_type = st.selectbox(
                "Task type",
                list(TASK_ICONS.keys()),
            )
            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High", "Critical"],
                index=1,
            )

        with right:
            due_date_value = st.date_input(
                "Deadline date",
                value=date.today() + timedelta(days=3),
                min_value=date.today(),
            )
            due_time_value = st.time_input(
                "Deadline time",
                value=time(23, 59),
            )
            estimated_hours = st.number_input(
                "Estimated study hours",
                min_value=0.5,
                max_value=100.0,
                value=2.0,
                step=0.5,
            )
            preferred_session = st.select_slider(
                "Preferred session length",
                options=[25, 30, 45, 60, 90, 120],
                value=60,
                format_func=lambda minutes: f"{minutes} minutes",
            )

        difficulty = st.slider(
            "Difficulty",
            1,
            5,
            3,
            help="Harder tasks receive slightly more scheduling priority.",
        )

        notes = st.text_area(
            "Notes",
            placeholder="Topics to review, materials needed, teacher instructions, etc.",
        )

        submitted = st.form_submit_button(
            "Add task",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not subject.strip() or not title.strip():
            st.error("Enter both a subject and a task name.")
        else:
            create_task(
                subject=subject,
                title=title,
                task_type=task_type,
                due_date=due_date_value,
                due_time=due_time_value,
                estimated_hours=estimated_hours,
                priority=priority,
                difficulty=difficulty,
                preferred_session_minutes=preferred_session,
                notes=notes,
            )
            st.success("Task added successfully.")


def manage_tasks_page(tasks: list[dict]) -> None:
    st.markdown(
        '<div class="section-title">Task manager</div>',
        unsafe_allow_html=True,
    )

    if not tasks:
        st.info("You have not added any tasks yet.")
        return

    f1, f2, f3 = st.columns([1, 1, 1.2])

    with f1:
        status_filter = st.selectbox(
            "Status",
            ["Active", "Completed", "All"],
        )

    with f2:
        sort_option = st.selectbox(
            "Sort by",
            ["Deadline", "Smart score", "Subject", "Priority"],
        )

    with f3:
        subject_options = ["All subjects"] + sorted(
            {task["subject"] for task in tasks}
        )
        subject_filter = st.selectbox("Subject", subject_options)

    filtered = tasks.copy()

    if status_filter == "Active":
        filtered = [task for task in filtered if not task["completed"]]
    elif status_filter == "Completed":
        filtered = [task for task in filtered if task["completed"]]

    if subject_filter != "All subjects":
        filtered = [
            task for task in filtered
            if task["subject"] == subject_filter
        ]

    if sort_option == "Deadline":
        filtered.sort(key=deadline_datetime)
    elif sort_option == "Smart score":
        filtered.sort(key=calculate_smart_score, reverse=True)
    elif sort_option == "Subject":
        filtered.sort(key=lambda task: task["subject"].lower())
    else:
        filtered.sort(
            key=lambda task: PRIORITY_WEIGHT.get(task["priority"], 0),
            reverse=True,
        )

    if not filtered:
        st.info("No tasks match the selected filters.")
        return

    st.dataframe(
        task_table(filtered),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown(
        '<div class="section-title">Edit selected task</div>',
        unsafe_allow_html=True,
    )

    task_lookup = {
        f"#{task['id']} — {task['subject']}: {task['title']}": task["id"]
        for task in filtered
    }
    selected_label = st.selectbox(
        "Choose a task",
        list(task_lookup.keys()),
    )
    task_id = task_lookup[selected_label]
    selected = read_task(task_id)

    if selected is None:
        st.error("Task could not be loaded.")
        return

    progress_fraction = (
        float(selected["completed_hours"])
        / float(selected["estimated_hours"])
    )
    st.progress(min(progress_fraction, 1.0))
    st.caption(
        f"{selected['completed_hours']:.1f} of "
        f"{selected['estimated_hours']:.1f} study hours completed"
    )

    tab_progress, tab_details = st.tabs(["Progress", "Task details"])

    with tab_progress:
        new_completed_hours = st.number_input(
            "Completed study hours",
            min_value=0.0,
            max_value=float(selected["estimated_hours"]),
            value=float(selected["completed_hours"]),
            step=0.5,
        )

        b1, b2, b3, b4 = st.columns(4)

        with b1:
            if st.button("Save progress", use_container_width=True):
                update_task_progress(task_id, new_completed_hours)
                st.success("Progress saved.")
                st.rerun()

        with b2:
            if st.button("Mark complete", use_container_width=True):
                set_task_completed(task_id, True)
                st.success("Task completed.")
                st.rerun()

        with b3:
            if st.button("Reopen", use_container_width=True):
                set_task_completed(task_id, False)
                st.success("Task reopened.")
                st.rerun()

        with b4:
            if st.button("Delete", use_container_width=True):
                remove_task(task_id)
                st.success("Task deleted.")
                st.rerun()

    with tab_details:
        with st.form("edit_task_form"):
            e1, e2 = st.columns(2)

            with e1:
                edited_subject = st.text_input(
                    "Subject",
                    value=selected["subject"],
                )
                edited_title = st.text_input(
                    "Task name",
                    value=selected["title"],
                )
                edited_priority = st.selectbox(
                    "Priority",
                    ["Low", "Medium", "High", "Critical"],
                    index=["Low", "Medium", "High", "Critical"].index(
                        selected["priority"]
                    ),
                )

            with e2:
                edited_due_date = st.date_input(
                    "Deadline date",
                    value=date.fromisoformat(selected["due_date"]),
                )
                edited_due_time = st.time_input(
                    "Deadline time",
                    value=time.fromisoformat(selected["due_time"]),
                )
                edited_hours = st.number_input(
                    "Estimated hours",
                    min_value=0.5,
                    max_value=100.0,
                    value=float(selected["estimated_hours"]),
                    step=0.5,
                )

            save_edits = st.form_submit_button(
                "Save task details",
                type="primary",
                use_container_width=True,
            )

        if save_edits:
            if not edited_subject.strip() or not edited_title.strip():
                st.error("Subject and task name cannot be empty.")
            else:
                update_task_details(
                    task_id=task_id,
                    subject=edited_subject,
                    title=edited_title,
                    due_date_value=edited_due_date,
                    due_time_value=edited_due_time,
                    priority=edited_priority,
                    estimated_hours=edited_hours,
                )
                st.success("Task details updated.")
                st.rerun()

    if selected["notes"]:
        st.info(f"Notes: {selected['notes']}")


def timetable_page(
    tasks: list[dict],
    availability: dict[str, dict],
) -> None:
    st.markdown(
        '<div class="section-title">Smart timetable generator</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "The planner ranks tasks by urgency, priority, difficulty, "
        "and remaining workload, then fits sessions into your available hours."
    )

    current_plan_days = int(get_setting("plan_days", "7"))
    current_break = int(get_setting("break_minutes", "10"))

    c1, c2 = st.columns(2)

    with c1:
        plan_days = st.select_slider(
            "Planning horizon",
            options=[7, 10, 14, 21],
            value=current_plan_days
            if current_plan_days in [7, 10, 14, 21]
            else 7,
            format_func=lambda value: f"{value} days",
        )

    with c2:
        break_minutes = st.select_slider(
            "Break between sessions",
            options=[0, 5, 10, 15, 20, 30],
            value=current_break
            if current_break in [0, 5, 10, 15, 20, 30]
            else 10,
            format_func=lambda value: f"{value} minutes",
        )

    set_setting("plan_days", str(plan_days))
    set_setting("break_minutes", str(break_minutes))

    active = [task for task in tasks if not task["completed"]]

    if not active:
        st.info("Add at least one active task to generate a timetable.")
        return

    schedule, warnings = build_smart_timetable(
        tasks=tasks,
        availability=availability,
        plan_days=plan_days,
        break_minutes=break_minutes,
    )

    if not schedule:
        st.warning(
            "No study sessions could be scheduled. "
            "Increase your available hours or change your study windows."
        )
        return

    total_minutes = sum(item["Minutes"] for item in schedule)
    covered_tasks = {item["Task ID"] for item in schedule}
    scheduled_days = {item["Date"] for item in schedule}

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Study sessions", len(schedule))
    m2.metric("Scheduled hours", f"{total_minutes / 60:.1f}")
    m3.metric("Tasks included", len(covered_tasks))
    m4.metric("Study days", len(scheduled_days))

    schedule_df = pd.DataFrame(schedule)
    export_df = schedule_df.copy()
    export_df["Date"] = pd.to_datetime(export_df["Date"]).dt.strftime(
        "%Y-%m-%d"
    )

    display_columns = [
        "Date", "Day", "Start", "End", "Subject", "Task",
        "Study Time", "Priority", "Urgency", "Reason",
    ]

    table_df = export_df[display_columns].copy()
    table_df["Date"] = pd.to_datetime(table_df["Date"]).dt.strftime(
        "%b %d, %Y"
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download timetable as CSV",
        data=export_df[display_columns].to_csv(index=False).encode("utf-8"),
        file_name="focusflow_study_timetable.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()
    st.markdown(
        '<div class="section-title">Daily schedule</div>',
        unsafe_allow_html=True,
    )

    schedule_by_date: dict[date, list[dict]] = {}
    for session in schedule:
        schedule_by_date.setdefault(session["Date"], []).append(session)

    day_tabs = st.tabs(
        [
            day_date.strftime("%a %b %d")
            for day_date in schedule_by_date.keys()
        ]
    )

    for tab, (day_date, sessions) in zip(
        day_tabs,
        schedule_by_date.items(),
    ):
        with tab:
            day_total = sum(session["Minutes"] for session in sessions)
            st.caption(
                f"{day_date.strftime('%A, %B %d')} · "
                f"{day_total / 60:.1f} scheduled hours"
            )

            for session in sessions:
                icon = TASK_ICONS.get(session["Type"], "📌")
                urgency_class = (
                    "badge-red"
                    if session["Urgency"] in {"Urgent", "Overdue"}
                    else "badge-orange"
                    if session["Urgency"] == "Due soon"
                    else "badge-green"
                )

                st.markdown(
                    f"""
                    <div class="session-row">
                        <div style="font-weight:760;">
                            {session["Start"]}–{session["End"]} ·
                            {icon} {session["Subject"]}
                        </div>
                        <div>{session["Task"]}</div>
                        <div style="margin-top:0.35rem;">
                            <span class="badge {urgency_class}">
                                {session["Urgency"]}
                            </span>
                            <span class="badge badge-purple">
                                {session["Study Time"]}
                            </span>
                        </div>
                        <div class="muted" style="margin-top:0.4rem;">
                            {session["Reason"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if warnings:
        st.divider()
        st.warning(
            "Some work did not fit into the available schedule."
        )
        for warning in warnings:
            st.write(f"• {warning}")
        st.caption(
            "Increase availability, extend the plan, reduce estimated hours, "
            "or update the deadline."
        )


def availability_page(availability: dict[str, dict]) -> None:
    st.markdown(
        '<div class="section-title">Weekly availability</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Set both your maximum study hours and the time window "
        "when you are normally free."
    )

    updated: dict[str, dict] = {}

    with st.form("availability_form"):
        for day_name in WEEKDAYS:
            values = availability[day_name]

            st.markdown(f"**{day_name}**")
            c1, c2, c3 = st.columns([1.2, 1, 1])

            with c1:
                hours = st.slider(
                    f"{day_name} hours",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(values["hours"]),
                    step=0.5,
                    label_visibility="collapsed",
                )

            with c2:
                start_value = st.time_input(
                    f"{day_name} start",
                    value=time.fromisoformat(values["start"]),
                    label_visibility="collapsed",
                )

            with c3:
                end_value = st.time_input(
                    f"{day_name} end",
                    value=time.fromisoformat(values["end"]),
                    label_visibility="collapsed",
                )

            updated[day_name] = {
                "hours": hours,
                "start": start_value.strftime("%H:%M"),
                "end": end_value.strftime("%H:%M"),
            }

        submitted = st.form_submit_button(
            "Save weekly availability",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        invalid_days = [
            day_name
            for day_name, values in updated.items()
            if time.fromisoformat(values["end"])
            <= time.fromisoformat(values["start"])
            and values["hours"] > 0
        ]

        if invalid_days:
            st.error(
                "The end time must be later than the start time for: "
                + ", ".join(invalid_days)
            )
        else:
            save_availability(updated)
            st.success("Availability saved.")
            st.rerun()

    st.divider()

    availability_rows = [
        {
            "Day": day_name,
            "Hours": values["hours"],
            "Study Window": (
                f"{time.fromisoformat(values['start']).strftime('%I:%M %p').lstrip('0')}"
                f" – "
                f"{time.fromisoformat(values['end']).strftime('%I:%M %p').lstrip('0')}"
            ),
        }
        for day_name, values in availability.items()
    ]

    st.dataframe(
        pd.DataFrame(availability_rows),
        use_container_width=True,
        hide_index=True,
    )

    chart_df = (
        pd.DataFrame(availability_rows)[["Day", "Hours"]]
        .set_index("Day")
    )
    st.bar_chart(chart_df)

    st.metric(
        "Total weekly study capacity",
        f"{sum(values['hours'] for values in availability.values()):.1f} hours",
    )


def about_page() -> None:
    st.markdown(
        '<div class="section-title">How the smart planner works</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **FocusFlow** creates a practical study plan using five pieces of information:

        1. **Deadline:** Work due sooner receives more urgency.
        2. **Priority:** High and critical tasks move ahead of lower-priority work.
        3. **Difficulty:** Difficult subjects are scheduled earlier.
        4. **Remaining workload:** Large unfinished tasks receive additional attention.
        5. **Availability:** Sessions never exceed the hours and time windows you set.

        Large tasks are broken into manageable sessions. The planner also adds optional
        breaks, flags work that cannot fit before its deadline, and recommends the best
        task to work on next.
        """
    )

    st.info(
        "All information is stored locally in focusflow.db. "
        "No account or internet connection is required after installation."
    )


# =========================================================
# MAIN APPLICATION
# =========================================================

initialize_database()
all_tasks = read_tasks(include_completed=True)
availability = read_availability()

with st.sidebar:
    st.markdown(
        f"""
        <div class="brand-card">
            <div class="brand-name">🎓 {APP_NAME}</div>
            <div class="brand-caption">Smart planning for better study habits</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Task",
            "Manage Tasks",
            "Smart Timetable",
            "Availability",
            "How It Works",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    active_count = sum(1 for task in all_tasks if not task["completed"])
    urgent_count = sum(
        1
        for task in all_tasks
        if not task["completed"] and days_left(task) <= 1
    )

    st.metric("Active tasks", active_count)
    st.metric("Urgent / overdue", urgent_count)

    st.caption("Data is saved automatically on this computer.")

render_hero()

if selected_page == "Dashboard":
    dashboard_page(all_tasks, availability)
elif selected_page == "Add Task":
    add_task_page()
elif selected_page == "Manage Tasks":
    manage_tasks_page(all_tasks)
elif selected_page == "Smart Timetable":
    timetable_page(all_tasks, availability)
elif selected_page == "Availability":
    availability_page(availability)
else:
    about_page()