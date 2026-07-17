from __future__ import annotations

import html
import sqlite3
import time as time_module
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------

APP_NAME = "StudyFlow"
DATABASE_FILE = Path("studyflow.db")

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

PRIORITY_POINTS = {
    "Low": 1,
    "Medium": 3,
    "High": 5,
}

st.set_page_config(
    page_title="StudyFlow",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CLEAN TEAL THEME
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        :root {
            --ink: #173b3f;
            --muted: #647b7d;
            --teal: #0f766e;
            --teal-dark: #115e59;
            --mint: #dff3ee;
            --cream: #fbfaf6;
            --card: rgba(255,255,255,0.88);
            --border: rgba(71, 104, 106, 0.17);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(20,184,166,0.09), transparent 25rem),
                radial-gradient(circle at top right, rgba(245,158,11,0.07), transparent 22rem),
                var(--cream);
        }

        .block-container {
            max-width: 1260px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #f1f7f5;
            border-right: 1px solid var(--border);
        }

        .brand {
            padding: 1.05rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #115e59, #0f766e);
            color: white;
            margin-bottom: 1.05rem;
            box-shadow: 0 10px 26px rgba(15,118,110,0.18);
        }

        .brand-title {
            font-size: 1.38rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            font-size: 0.82rem;
            opacity: 0.88;
            margin-top: 0.22rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.35rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            border: 1px solid transparent;
            border-radius: 12px;
            padding: 0.5rem 0.65rem;
            margin: 0;
            transition: 0.15s ease;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background: rgba(15,118,110,0.08);
            border-color: rgba(15,118,110,0.12);
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
            background: white;
            border-color: rgba(15,118,110,0.22);
            box-shadow: 0 4px 12px rgba(15,118,110,0.08);
        }

        .hero {
            padding: 1.35rem 1.45rem;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: var(--card);
            margin-bottom: 1.2rem;
            box-shadow: 0 8px 24px rgba(23,59,63,0.04);
        }

        .hero h1 {
            color: var(--ink);
            font-size: 2rem;
            margin: 0;
            letter-spacing: -0.035em;
        }

        .hero p {
            color: var(--muted);
            margin: 0.45rem 0 0;
        }

        .task-card {
            padding: 0.95rem 1rem;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: var(--card);
            margin-bottom: 0.68rem;
            box-shadow: 0 4px 14px rgba(23,59,63,0.025);
        }

        .urgent { border-left: 6px solid #e85d5d; }
        .soon { border-left: 6px solid #e6a23c; }
        .normal { border-left: 6px solid #2f9e82; }
        .overdue { border-left: 6px solid #9f3030; }

        .task-title {
            color: var(--ink);
            font-weight: 760;
            font-size: 1rem;
        }

        .task-meta {
            color: var(--muted);
            font-size: 0.87rem;
            margin-top: 0.3rem;
        }

        .badge {
            display: inline-block;
            margin-top: 0.45rem;
            margin-right: 0.25rem;
            padding: 0.2rem 0.52rem;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
        }

        .red { color: #8f2525; background: #fde3e3; }
        .orange { color: #8b5412; background: #fff0cf; }
        .green { color: #0f6653; background: #dff3ee; }
        .teal { color: #115e59; background: #d5efeb; }
        .gray { color: #475569; background: #e8eeed; }

        .next-task {
            padding: 1.15rem;
            border-radius: 17px;
            color: white;
            background: linear-gradient(135deg, #115e59, #168f83);
            box-shadow: 0 12px 28px rgba(15,118,110,0.18);
        }

        .timer-card {
            text-align: center;
            padding: 1.55rem 1rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: var(--card);
            box-shadow: 0 12px 32px rgba(23,59,63,0.06);
            margin: 0.75rem 0;
        }

        .timer-task {
            color: var(--muted);
            font-size: 0.92rem;
            font-weight: 650;
        }

        .timer-display {
            color: var(--ink);
            font-size: clamp(3.4rem, 9vw, 6rem);
            line-height: 1;
            font-weight: 850;
            letter-spacing: -0.06em;
            margin: 0.55rem 0;
            font-variant-numeric: tabular-nums;
        }

        .timer-status {
            color: var(--teal);
            font-size: 0.9rem;
            font-weight: 720;
        }

        .session-card {
            padding: 0.8rem 0.9rem;
            border-radius: 13px;
            background: #f2f7f5;
            border: 1px solid var(--border);
            margin: 0.45rem 0;
        }

        div[data-testid="stMetric"] {
            padding: 0.88rem;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: var(--card);
            box-shadow: 0 4px 14px rgba(23,59,63,0.025);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 11px;
            font-weight: 680;
            min-height: 2.6rem;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input {
            border-radius: 10px;
        }

        div[data-baseweb="select"] > div {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATABASE FUNCTIONS
# ---------------------------------------------------------

def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                task_name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                hours_needed REAL NOT NULL,
                studied_hours REAL NOT NULL DEFAULT 0,
                priority TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        task_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
        }

        if "studied_hours" not in task_columns:
            connection.execute(
                """
                ALTER TABLE tasks
                ADD COLUMN studied_hours REAL NOT NULL DEFAULT 0
                """
            )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS availability (
                day_name TEXT PRIMARY KEY,
                study_hours REAL NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                minutes INTEGER NOT NULL,
                completed_at TEXT NOT NULL
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

        for day_name in DAYS:
            default_hours = 2.0 if day_name not in {"Saturday", "Sunday"} else 3.0
            connection.execute(
                """
                INSERT OR IGNORE INTO availability (day_name, study_hours)
                VALUES (?, ?)
                """,
                (day_name, default_hours),
            )

        connection.execute(
            """
            INSERT OR IGNORE INTO settings (setting_key, setting_value)
            VALUES ('daily_focus_goal', '60')
            """
        )


def add_task(
    subject: str,
    task_name: str,
    due_date_value: date,
    hours_needed: float,
    priority: str,
) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO tasks (
                subject,
                task_name,
                due_date,
                hours_needed,
                studied_hours,
                priority,
                completed
            )
            VALUES (?, ?, ?, ?, 0, ?, 0)
            """,
            (
                subject.strip(),
                task_name.strip(),
                due_date_value.isoformat(),
                float(hours_needed),
                priority,
            ),
        )


def get_tasks() -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM tasks
            ORDER BY completed ASC, due_date ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return dict(row) if row else None


def mark_complete(task_id: int) -> None:
    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed = 1,
                studied_hours = hours_needed
            WHERE id = ?
            """,
            (task_id,),
        )


def reopen_task(task_id: int) -> None:
    task = get_task(task_id)
    if task is None:
        return

    studied_hours = float(task["studied_hours"])
    hours_needed = float(task["hours_needed"])

    if studied_hours >= hours_needed:
        studied_hours = max(0.0, hours_needed - 0.5)

    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed = 0,
                studied_hours = ?
            WHERE id = ?
            """,
            (studied_hours, task_id),
        )


def update_task_progress(task_id: int, studied_hours: float) -> None:
    task = get_task(task_id)
    if task is None:
        return

    hours_needed = float(task["hours_needed"])
    safe_hours = max(0.0, min(float(studied_hours), hours_needed))
    completed = int(safe_hours >= hours_needed)

    with connect() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET studied_hours = ?,
                completed = ?
            WHERE id = ?
            """,
            (safe_hours, completed, task_id),
        )


def delete_task(task_id: int) -> None:
    with connect() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )


def get_availability() -> dict[str, float]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT day_name, study_hours FROM availability"
        ).fetchall()

    saved = {
        row["day_name"]: float(row["study_hours"])
        for row in rows
    }

    return {
        day_name: saved.get(day_name, 0.0)
        for day_name in DAYS
    }


def save_availability(availability: dict[str, float]) -> None:
    with connect() as connection:
        for day_name, hours in availability.items():
            connection.execute(
                """
                INSERT INTO availability (day_name, study_hours)
                VALUES (?, ?)
                ON CONFLICT(day_name)
                DO UPDATE SET study_hours = excluded.study_hours
                """,
                (day_name, float(hours)),
            )


def get_setting(key: str, fallback: str) -> str:
    with connect() as connection:
        row = connection.execute(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,),
        ).fetchone()

    return str(row["setting_value"]) if row else fallback


def save_setting(key: str, value: str) -> None:
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


def record_focus_session(task_id: int, minutes: int) -> None:
    task = get_task(task_id)
    if task is None or minutes <= 0:
        return

    new_studied_hours = min(
        float(task["hours_needed"]),
        float(task["studied_hours"]) + minutes / 60,
    )
    completed = int(new_studied_hours >= float(task["hours_needed"]))

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO focus_sessions (task_id, minutes, completed_at)
            VALUES (?, ?, ?)
            """,
            (
                task_id,
                int(minutes),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        connection.execute(
            """
            UPDATE tasks
            SET studied_hours = ?,
                completed = ?
            WHERE id = ?
            """,
            (new_studied_hours, completed, task_id),
        )


def get_today_focus_stats() -> tuple[int, int]:
    today_text = date.today().isoformat()

    with connect() as connection:
        row = connection.execute(
            """
            SELECT
                COALESCE(SUM(minutes), 0) AS total_minutes,
                COUNT(*) AS session_count
            FROM focus_sessions
            WHERE DATE(completed_at) = ?
            """,
            (today_text,),
        ).fetchone()

    return int(row["total_minutes"]), int(row["session_count"])


def get_recent_focus_sessions(limit: int = 6) -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT
                focus_sessions.minutes,
                focus_sessions.completed_at,
                tasks.subject,
                tasks.task_name
            FROM focus_sessions
            LEFT JOIN tasks ON tasks.id = focus_sessions.task_id
            ORDER BY focus_sessions.completed_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# SMART PLANNER LOGIC
# ---------------------------------------------------------

def remaining_task_hours(task: dict) -> float:
    return max(
        0.0,
        float(task["hours_needed"]) - float(task["studied_hours"]),
    )


def task_progress(task: dict) -> float:
    hours_needed = float(task["hours_needed"])

    if hours_needed <= 0:
        return 0.0

    return min(1.0, float(task["studied_hours"]) / hours_needed)


def days_remaining(task: dict) -> int:
    due_date_value = date.fromisoformat(task["due_date"])
    return (due_date_value - date.today()).days


def urgency(task: dict) -> tuple[str, str, str]:
    days_left = days_remaining(task)

    if days_left < 0:
        return "Overdue", "overdue", "red"
    if days_left <= 1:
        return "Urgent", "urgent", "red"
    if days_left <= 3:
        return "Due soon", "soon", "orange"
    return "On track", "normal", "green"


def smart_score(task: dict) -> float:
    days_left = days_remaining(task)

    if days_left < 0:
        urgency_score = 20
    else:
        urgency_score = 10 / (days_left + 1)

    priority_score = PRIORITY_POINTS[task["priority"]] * 2
    workload_score = remaining_task_hours(task) * 0.5

    return round(urgency_score + priority_score + workload_score, 2)


def generate_weekly_plan(
    tasks: list[dict],
    availability: dict[str, float],
) -> tuple[list[dict], list[str]]:
    today = date.today()
    plan_dates = [today + timedelta(days=offset) for offset in range(7)]

    available_hours = {
        plan_date: availability[plan_date.strftime("%A")]
        for plan_date in plan_dates
    }

    active_tasks = [
        task.copy()
        for task in tasks
        if not task["completed"] and remaining_task_hours(task) > 0
    ]

    for task in active_tasks:
        task["remaining_hours"] = remaining_task_hours(task)
        task["score"] = smart_score(task)

    active_tasks.sort(
        key=lambda task: (-task["score"], task["due_date"])
    )

    schedule: list[dict] = []
    warnings: list[str] = []

    for task in active_tasks:
        due_date_value = date.fromisoformat(task["due_date"])

        if due_date_value < today:
            allowed_dates = plan_dates
        else:
            allowed_dates = [
                plan_date
                for plan_date in plan_dates
                if plan_date <= due_date_value
            ]

        while task["remaining_hours"] > 0:
            possible_dates = [
                plan_date
                for plan_date in allowed_dates
                if available_hours[plan_date] > 0
            ]

            if not possible_dates:
                break

            chosen_date = possible_dates[0]

            session_hours = min(
                1.0,
                task["remaining_hours"],
                available_hours[chosen_date],
            )

            schedule.append(
                {
                    "Date": chosen_date,
                    "Day": chosen_date.strftime("%A"),
                    "Subject": task["subject"],
                    "Task": task["task_name"],
                    "Study Time": f"{session_hours:.1f} hr",
                    "Priority": task["priority"],
                    "Status": urgency(task)[0],
                }
            )

            task["remaining_hours"] -= session_hours
            available_hours[chosen_date] -= session_hours

        if task["remaining_hours"] > 0:
            warnings.append(
                f"{task['subject']} — {task['task_name']} still needs "
                f"{task['remaining_hours']:.1f} hour(s)."
            )

    schedule.sort(key=lambda row: row["Date"])
    return schedule, warnings


# ---------------------------------------------------------
# TIMER STATE AND LIVE TIMER
# ---------------------------------------------------------

def initialize_timer_state() -> None:
    defaults = {
        "timer_running": False,
        "timer_end_timestamp": 0.0,
        "timer_remaining_seconds": 25 * 60,
        "timer_duration_minutes": 25,
        "timer_task_id": None,
        "timer_config": None,
        "timer_logged": False,
        "timer_complete_notice": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.fragment(run_every="1s")
def render_live_timer() -> None:
    if st.session_state.timer_running:
        remaining_seconds = max(
            0,
            int(
                round(
                    st.session_state.timer_end_timestamp
                    - time_module.time()
                )
            ),
        )
        st.session_state.timer_remaining_seconds = remaining_seconds
    else:
        remaining_seconds = int(
            st.session_state.timer_remaining_seconds
        )

    if (
        remaining_seconds <= 0
        and not st.session_state.timer_logged
        and st.session_state.timer_task_id is not None
    ):
        st.session_state.timer_running = False
        st.session_state.timer_remaining_seconds = 0
        record_focus_session(
            int(st.session_state.timer_task_id),
            int(st.session_state.timer_duration_minutes),
        )
        st.session_state.timer_logged = True
        st.session_state.timer_complete_notice = True

    duration_seconds = max(
        1,
        int(st.session_state.timer_duration_minutes) * 60,
    )
    progress = 1 - remaining_seconds / duration_seconds
    progress = min(1.0, max(0.0, progress))

    minutes, seconds = divmod(remaining_seconds, 60)
    selected_task = (
        get_task(int(st.session_state.timer_task_id))
        if st.session_state.timer_task_id is not None
        else None
    )

    if selected_task:
        task_text = (
            f"{html.escape(selected_task['subject'])}: "
            f"{html.escape(selected_task['task_name'])}"
        )
    else:
        task_text = "Choose a task to begin"

    status_text = (
        "Focus session in progress"
        if st.session_state.timer_running
        else "Ready when you are"
    )

    if remaining_seconds == 0:
        status_text = "Session complete"

    st.markdown(
        f"""
        <div class="timer-card">
            <div class="timer-task">{task_text}</div>
            <div class="timer-display">{minutes:02d}:{seconds:02d}</div>
            <div class="timer-status">{status_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress)

    if st.session_state.timer_complete_notice:
        st.success(
            "Focus session completed and added to the task's progress."
        )


# ---------------------------------------------------------
# UI HELPERS
# ---------------------------------------------------------

def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🌿 StudyFlow</h1>
            <p>A calm, simple place to organize tasks, focus, and follow a realistic study plan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task: dict) -> None:
    label, card_class, badge_class = urgency(task)
    due_date_text = date.fromisoformat(task["due_date"]).strftime("%b %d, %Y")
    progress_percent = task_progress(task) * 100

    safe_subject = html.escape(str(task["subject"]))
    safe_name = html.escape(str(task["task_name"]))

    st.markdown(
        f"""
        <div class="task-card {card_class}">
            <div class="task-title">
                {safe_subject}: {safe_name}
            </div>
            <div class="task-meta">
                Due {due_date_text} · {remaining_task_hours(task):.1f} hours remaining
                · {progress_percent:.0f}% complete
            </div>
            <span class="badge {badge_class}">{label}</span>
            <span class="badge teal">{task["priority"]} priority</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# PAGES
# ---------------------------------------------------------

def dashboard_page(tasks: list[dict], availability: dict[str, float]) -> None:
    active_tasks = [task for task in tasks if not task["completed"]]
    completed_tasks = [task for task in tasks if task["completed"]]
    urgent_tasks = [
        task for task in active_tasks
        if days_remaining(task) <= 1
    ]

    remaining_hours = sum(
        remaining_task_hours(task)
        for task in active_tasks
    )

    today_minutes, today_sessions = get_today_focus_stats()
    daily_goal = int(get_setting("daily_focus_goal", "60"))

    st.subheader("Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active tasks", len(active_tasks))
    m2.metric("Hours remaining", f"{remaining_hours:.1f}")
    m3.metric("Urgent / overdue", len(urgent_tasks))
    m4.metric("Focused today", f"{today_minutes} min")

    goal_progress = min(1.0, today_minutes / max(daily_goal, 1))
    st.caption(f"Daily focus goal: {today_minutes} of {daily_goal} minutes")
    st.progress(goal_progress)

    if tasks:
        completion = len(completed_tasks) / len(tasks)
        st.caption(f"Task completion: {completion * 100:.0f}%")
        st.progress(completion)

    st.divider()

    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("Study next")

        if not active_tasks:
            st.info("Add a task to receive a recommendation.")
        else:
            best_task = max(active_tasks, key=smart_score)
            safe_subject = html.escape(str(best_task["subject"]))
            safe_name = html.escape(str(best_task["task_name"]))

            st.markdown(
                f"""
                <div class="next-task">
                    <div style="font-size:0.8rem;opacity:0.85;">
                        RECOMMENDED NEXT
                    </div>
                    <div style="font-size:1.25rem;font-weight:800;margin-top:0.3rem;">
                        {safe_subject}: {safe_name}
                    </div>
                    <div style="margin-top:0.45rem;">
                        Due {date.fromisoformat(best_task["due_date"]).strftime("%b %d")}
                        · {best_task["priority"]} priority
                        · {remaining_task_hours(best_task):.1f} hours left
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Today's focus")
        st.metric("Completed sessions", today_sessions)
        if today_minutes >= daily_goal:
            st.success("Daily focus goal reached.")
        elif today_sessions == 0:
            st.info("Start a focus timer session when you are ready.")
        else:
            st.info(f"{daily_goal - today_minutes} minutes left to reach your goal.")

    st.divider()
    st.subheader("Upcoming tasks")

    if not active_tasks:
        st.info("No active tasks.")
    else:
        for task in sorted(
            active_tasks,
            key=lambda item: item["due_date"],
        )[:6]:
            render_task_card(task)


def add_task_page() -> None:
    st.subheader("Add a Task")
    st.caption("Enter only the information needed to build your schedule.")

    with st.form("add_task_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
            subject = st.text_input(
                "Subject",
                placeholder="Example: Math",
            )
            task_name = st.text_input(
                "Task name",
                placeholder="Example: Study for Chapter 5 test",
            )
            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"],
                index=1,
            )

        with right:
            due_date_value = st.date_input(
                "Deadline",
                value=date.today() + timedelta(days=3),
                min_value=date.today(),
            )
            hours_needed = st.number_input(
                "Study hours needed",
                min_value=0.5,
                max_value=40.0,
                value=2.0,
                step=0.5,
            )

        submitted = st.form_submit_button(
            "Add task",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not subject.strip() or not task_name.strip():
            st.error("Enter both a subject and task name.")
        else:
            add_task(
                subject=subject,
                task_name=task_name,
                due_date_value=due_date_value,
                hours_needed=hours_needed,
                priority=priority,
            )
            st.success("Task added successfully.")


def my_tasks_page(tasks: list[dict]) -> None:
    st.subheader("My Tasks")

    if not tasks:
        st.info("No tasks have been added yet.")
        return

    filter_1, filter_2 = st.columns([1, 1.5])

    with filter_1:
        status_filter = st.selectbox(
            "Show",
            ["Active tasks", "Completed tasks", "All tasks"],
        )

    with filter_2:
        search_text = st.text_input(
            "Search",
            placeholder="Search subject or task...",
        ).strip().lower()

    if status_filter == "Active tasks":
        filtered_tasks = [
            task for task in tasks if not task["completed"]
        ]
    elif status_filter == "Completed tasks":
        filtered_tasks = [
            task for task in tasks if task["completed"]
        ]
    else:
        filtered_tasks = tasks

    if search_text:
        filtered_tasks = [
            task
            for task in filtered_tasks
            if search_text in task["subject"].lower()
            or search_text in task["task_name"].lower()
        ]

    if not filtered_tasks:
        st.info("No tasks match this filter.")
        return

    rows = []

    for task in filtered_tasks:
        rows.append(
            {
                "Subject": task["subject"],
                "Task": task["task_name"],
                "Deadline": date.fromisoformat(
                    task["due_date"]
                ).strftime("%b %d, %Y"),
                "Remaining": f"{remaining_task_hours(task):.1f} hr",
                "Progress": f"{task_progress(task) * 100:.0f}%",
                "Priority": task["priority"],
                "Status": (
                    "Completed"
                    if task["completed"]
                    else urgency(task)[0]
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Update a Task")

    task_options = {
        f"{task['subject']}: {task['task_name']}": task["id"]
        for task in filtered_tasks
    }

    selected_label = st.selectbox(
        "Choose a task",
        list(task_options.keys()),
    )
    selected_id = task_options[selected_label]
    selected_task = get_task(selected_id)

    if selected_task is None:
        st.error("The task could not be loaded.")
        return

    st.progress(task_progress(selected_task))
    st.caption(
        f"{selected_task['studied_hours']:.1f} of "
        f"{selected_task['hours_needed']:.1f} hours completed"
    )

    studied_hours = st.number_input(
        "Hours studied",
        min_value=0.0,
        max_value=float(selected_task["hours_needed"]),
        value=float(selected_task["studied_hours"]),
        step=0.5,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("Save progress", use_container_width=True):
            update_task_progress(selected_id, studied_hours)
            st.success("Progress saved.")
            st.rerun()

    with c2:
        if st.button("Complete", use_container_width=True):
            mark_complete(selected_id)
            st.success("Task completed.")
            st.rerun()

    with c3:
        if st.button("Reopen", use_container_width=True):
            reopen_task(selected_id)
            st.success("Task reopened.")
            st.rerun()

    with c4:
        if st.button("Delete", use_container_width=True):
            delete_task(selected_id)
            st.success("Task deleted.")
            st.rerun()


def focus_timer_page(tasks: list[dict]) -> None:
    initialize_timer_state()

    st.subheader("Focus Timer")
    st.caption(
        "Choose a task and complete a focused study session. "
        "Finished sessions automatically update task progress."
    )

    active_tasks = [
        task for task in tasks
        if not task["completed"] and remaining_task_hours(task) > 0
    ]

    if not active_tasks:
        st.info("Add or reopen a task before starting the timer.")
        return

    task_options = {
        f"{task['subject']}: {task['task_name']} "
        f"({remaining_task_hours(task):.1f} hr left)": task["id"]
        for task in active_tasks
    }

    left, right = st.columns([1.4, 1])

    with left:
        selected_label = st.selectbox(
            "Focus task",
            list(task_options.keys()),
            disabled=st.session_state.timer_running,
        )
        selected_task_id = task_options[selected_label]

    with right:
        selected_duration = st.selectbox(
            "Session length",
            [15, 25, 45, 60],
            index=1,
            format_func=lambda value: f"{value} minutes",
            disabled=st.session_state.timer_running,
        )

    config = (selected_task_id, selected_duration)

    if (
        not st.session_state.timer_running
        and st.session_state.timer_config != config
    ):
        st.session_state.timer_config = config
        st.session_state.timer_task_id = selected_task_id
        st.session_state.timer_duration_minutes = selected_duration
        st.session_state.timer_remaining_seconds = selected_duration * 60
        st.session_state.timer_logged = False
        st.session_state.timer_complete_notice = False

    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button(
            "▶ Start",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.timer_running,
        ):
            if st.session_state.timer_remaining_seconds <= 0:
                st.session_state.timer_remaining_seconds = (
                    selected_duration * 60
                )

            st.session_state.timer_task_id = selected_task_id
            st.session_state.timer_duration_minutes = selected_duration
            st.session_state.timer_end_timestamp = (
                time_module.time()
                + st.session_state.timer_remaining_seconds
            )
            st.session_state.timer_running = True
            st.session_state.timer_logged = False
            st.session_state.timer_complete_notice = False
            st.rerun()

    with b2:
        if st.button(
            "⏸ Pause",
            use_container_width=True,
            disabled=not st.session_state.timer_running,
        ):
            st.session_state.timer_remaining_seconds = max(
                0,
                int(
                    round(
                        st.session_state.timer_end_timestamp
                        - time_module.time()
                    )
                ),
            )
            st.session_state.timer_running = False
            st.rerun()

    with b3:
        if st.button(
            "↺ Reset",
            use_container_width=True,
        ):
            st.session_state.timer_running = False
            st.session_state.timer_remaining_seconds = (
                selected_duration * 60
            )
            st.session_state.timer_duration_minutes = selected_duration
            st.session_state.timer_task_id = selected_task_id
            st.session_state.timer_logged = False
            st.session_state.timer_complete_notice = False
            st.rerun()

    render_live_timer()

    st.divider()

    today_minutes, today_sessions = get_today_focus_stats()
    daily_goal = int(get_setting("daily_focus_goal", "60"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Focused today", f"{today_minutes} min")
    c2.metric("Sessions today", today_sessions)
    c3.metric(
        "Goal remaining",
        f"{max(0, daily_goal - today_minutes)} min",
    )

    new_goal = st.select_slider(
        "Daily focus goal",
        options=[30, 45, 60, 90, 120, 180],
        value=daily_goal
        if daily_goal in [30, 45, 60, 90, 120, 180]
        else 60,
        format_func=lambda value: f"{value} minutes",
    )

    if new_goal != daily_goal:
        save_setting("daily_focus_goal", str(new_goal))
        st.rerun()

    recent_sessions = get_recent_focus_sessions()

    if recent_sessions:
        st.subheader("Recent focus sessions")

        for session in recent_sessions:
            completed_at = datetime.fromisoformat(
                session["completed_at"]
            ).strftime("%b %d · %I:%M %p")
            subject = html.escape(session["subject"] or "Deleted task")
            task_name = html.escape(session["task_name"] or "Task removed")

            st.markdown(
                f"""
                <div class="session-card">
                    <strong>{subject}: {task_name}</strong><br>
                    <span style="color:#647b7d;">
                        {session["minutes"]} minutes · {completed_at}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def study_plan_page(
    tasks: list[dict],
    availability: dict[str, float],
) -> None:
    st.subheader("Study Plan")
    st.caption(
        "Set your available hours, then the app will build a seven-day timetable."
    )

    with st.expander("Available study hours", expanded=False):
        with st.form("availability_form"):
            updated_hours: dict[str, float] = {}

            left, right = st.columns(2)

            for index, day_name in enumerate(DAYS):
                target = left if index < 4 else right

                with target:
                    updated_hours[day_name] = st.slider(
                        day_name,
                        min_value=0.0,
                        max_value=8.0,
                        value=float(availability[day_name]),
                        step=0.5,
                    )

            save_hours = st.form_submit_button(
                "Save available hours",
                type="primary",
                use_container_width=True,
            )

        if save_hours:
            save_availability(updated_hours)
            st.success("Available hours saved.")
            st.rerun()

    active_tasks = [
        task
        for task in tasks
        if not task["completed"] and remaining_task_hours(task) > 0
    ]

    if not active_tasks:
        st.info("Add at least one active task to generate a plan.")
        return

    schedule, warnings = generate_weekly_plan(
        tasks,
        availability,
    )

    if not schedule:
        st.warning(
            "No sessions could be scheduled. Add available study hours."
        )
        return

    total_hours = sum(
        float(row["Study Time"].replace(" hr", ""))
        for row in schedule
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Study sessions", len(schedule))
    c2.metric("Scheduled hours", f"{total_hours:.1f}")
    c3.metric(
        "Tasks included",
        len({row["Task"] for row in schedule}),
    )

    display_rows = []

    for row in schedule:
        display_rows.append(
            {
                "Date": row["Date"].strftime("%b %d, %Y"),
                "Day": row["Day"],
                "Subject": row["Subject"],
                "Task": row["Task"],
                "Study Time": row["Study Time"],
                "Priority": row["Priority"],
                "Status": row["Status"],
            }
        )

    schedule_df = pd.DataFrame(display_rows)

    st.dataframe(
        schedule_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download study plan",
        data=schedule_df.to_csv(index=False).encode("utf-8"),
        file_name="studyflow_weekly_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Day-by-day view")

    for plan_date, sessions in schedule_df.groupby(
        ["Date", "Day"],
        sort=False,
    ):
        date_text, day_text = plan_date

        with st.expander(f"{day_text}, {date_text}"):
            for _, session in sessions.iterrows():
                safe_subject = html.escape(str(session["Subject"]))
                safe_task = html.escape(str(session["Task"]))

                st.markdown(
                    f"""
                    <div class="session-card">
                        <strong>{safe_subject}: {safe_task}</strong><br>
                        <span style="color:#647b7d;">
                            {session["Study Time"]} ·
                            {session["Priority"]} priority ·
                            {session["Status"]}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if warnings:
        st.warning("Some work did not fit into the available hours.")
        for warning in warnings:
            st.write(f"• {warning}")


# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------

initialize_database()
initialize_timer_state()

tasks = get_tasks()
availability = get_availability()

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">🌿 StudyFlow</div>
            <div class="brand-subtitle">Plan clearly. Focus calmly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Task",
            "✅ My Tasks",
            "⏱️ Focus Timer",
            "🗓️ Study Plan",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    active_count = len([
        task for task in tasks if not task["completed"]
    ])

    urgent_count = len([
        task
        for task in tasks
        if not task["completed"] and days_remaining(task) <= 1
    ])

    today_minutes, _ = get_today_focus_stats()

    st.metric("Active tasks", active_count)
    st.metric("Urgent / overdue", urgent_count)
    st.metric("Focused today", f"{today_minutes} min")

render_header()

if page == "🏠 Dashboard":
    dashboard_page(tasks, availability)
elif page == "➕ Add Task":
    add_task_page()
elif page == "✅ My Tasks":
    my_tasks_page(tasks)
elif page == "⏱️ Focus Timer":
    focus_timer_page(tasks)
else:
    study_plan_page(tasks, availability)