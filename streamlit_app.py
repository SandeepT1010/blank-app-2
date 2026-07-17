from __future__ import annotations

import sqlite3
from datetime import date, timedelta
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
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CLEAN STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1250px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(100, 116, 139, 0.18);
        }

        .brand {
            padding: 1rem;
            border-radius: 16px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            color: white;
            margin-bottom: 1rem;
        }

        .brand-title {
            font-size: 1.35rem;
            font-weight: 800;
        }

        .brand-subtitle {
            font-size: 0.82rem;
            opacity: 0.88;
            margin-top: 0.2rem;
        }

        .hero {
            padding: 1.3rem 1.4rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-radius: 18px;
            background: rgba(255,255,255,0.78);
            margin-bottom: 1.2rem;
        }

        .hero h1 {
            font-size: 2rem;
            margin: 0;
        }

        .hero p {
            color: #64748b;
            margin: 0.45rem 0 0;
        }

        .task-card {
            padding: 0.9rem 1rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-radius: 14px;
            background: rgba(255,255,255,0.82);
            margin-bottom: 0.65rem;
        }

        .urgent {
            border-left: 6px solid #ef4444;
        }

        .soon {
            border-left: 6px solid #f59e0b;
        }

        .normal {
            border-left: 6px solid #10b981;
        }

        .overdue {
            border-left: 6px solid #991b1b;
        }

        .task-title {
            font-weight: 750;
            font-size: 1rem;
        }

        .task-meta {
            color: #64748b;
            font-size: 0.88rem;
            margin-top: 0.3rem;
        }

        .badge {
            display: inline-block;
            margin-top: 0.45rem;
            margin-right: 0.25rem;
            padding: 0.2rem 0.52rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .red {
            color: #991b1b;
            background: #fee2e2;
        }

        .orange {
            color: #92400e;
            background: #fef3c7;
        }

        .green {
            color: #065f46;
            background: #d1fae5;
        }

        .blue {
            color: #1e40af;
            background: #dbeafe;
        }

        .gray {
            color: #334155;
            background: #e2e8f0;
        }

        .next-task {
            padding: 1.1rem;
            border-radius: 16px;
            color: white;
            background: linear-gradient(135deg, #4338ca, #2563eb);
        }

        div[data-testid="stMetric"] {
            padding: 0.85rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-radius: 14px;
            background: rgba(255,255,255,0.8);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 650;
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
                priority TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
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

        for day_name in DAYS:
            default_hours = 2.0 if day_name not in {"Saturday", "Sunday"} else 3.0
            connection.execute(
                """
                INSERT OR IGNORE INTO availability (day_name, study_hours)
                VALUES (?, ?)
                """,
                (day_name, default_hours),
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
                priority,
                completed
            )
            VALUES (?, ?, ?, ?, ?, 0)
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


def mark_complete(task_id: int) -> None:
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,),
        )


def reopen_task(task_id: int) -> None:
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET completed = 0 WHERE id = ?",
            (task_id,),
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


# ---------------------------------------------------------
# SMART PLANNER LOGIC
# ---------------------------------------------------------

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
    workload_score = float(task["hours_needed"]) * 0.5

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
        if not task["completed"]
    ]

    for task in active_tasks:
        task["remaining_hours"] = float(task["hours_needed"])
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
# UI HELPERS
# ---------------------------------------------------------

def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>📘 StudyFlow</h1>
            <p>Add your tasks, set your available hours, and get a realistic weekly study plan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task: dict) -> None:
    label, card_class, badge_class = urgency(task)
    due_date_text = date.fromisoformat(task["due_date"]).strftime("%b %d, %Y")

    st.markdown(
        f"""
        <div class="task-card {card_class}">
            <div class="task-title">
                {task["subject"]}: {task["task_name"]}
            </div>
            <div class="task-meta">
                Due {due_date_text} · {task["hours_needed"]:.1f} study hours
            </div>
            <span class="badge {badge_class}">{label}</span>
            <span class="badge blue">{task["priority"]} priority</span>
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
        float(task["hours_needed"])
        for task in active_tasks
    )

    weekly_hours = sum(availability.values())

    st.subheader("Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active tasks", len(active_tasks))
    m2.metric("Study hours needed", f"{remaining_hours:.1f}")
    m3.metric("Urgent / overdue", len(urgent_tasks))
    m4.metric("Weekly availability", f"{weekly_hours:.1f} hr")

    if tasks:
        completion = len(completed_tasks) / len(tasks)
        st.caption("Task completion")
        st.progress(completion)
        st.caption(f"{completion * 100:.0f}% completed")

    st.divider()

    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("What should I study next?")

        if not active_tasks:
            st.info("Add a task to receive a recommendation.")
        else:
            best_task = max(active_tasks, key=smart_score)

            st.markdown(
                f"""
                <div class="next-task">
                    <div style="font-size:0.8rem;opacity:0.85;">
                        RECOMMENDED NEXT
                    </div>
                    <div style="font-size:1.25rem;font-weight:800;margin-top:0.3rem;">
                        {best_task["subject"]}: {best_task["task_name"]}
                    </div>
                    <div style="margin-top:0.45rem;">
                        Due {date.fromisoformat(best_task["due_date"]).strftime("%b %d")}
                        · {best_task["priority"]} priority
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("How to use the app")
        st.write("**1.** Add your assignments and exams.")
        st.write("**2.** Set the hours you can study each day.")
        st.write("**3.** Open Study Plan to see your timetable.")
        st.write("**4.** Mark tasks complete when finished.")

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

    status_filter = st.selectbox(
        "Show",
        ["Active tasks", "Completed tasks", "All tasks"],
    )

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
                "Hours": task["hours_needed"],
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

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Mark complete", use_container_width=True):
            mark_complete(selected_id)
            st.success("Task completed.")
            st.rerun()

    with c2:
        if st.button("Reopen task", use_container_width=True):
            reopen_task(selected_id)
            st.success("Task reopened.")
            st.rerun()

    with c3:
        if st.button("Delete task", use_container_width=True):
            delete_task(selected_id)
            st.success("Task deleted.")
            st.rerun()


def study_plan_page(
    tasks: list[dict],
    availability: dict[str, float],
) -> None:
    st.subheader("Study Plan")
    st.caption(
        "Set your available hours, then the app will build a seven-day timetable."
    )

    with st.expander("Set available study hours", expanded=True):
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
        task for task in tasks if not task["completed"]
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

    if warnings:
        st.warning("Some work did not fit into the available hours.")
        for warning in warnings:
            st.write(f"• {warning}")


# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------

initialize_database()

tasks = get_tasks()
availability = get_availability()

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">📘 StudyFlow</div>
            <div class="brand-subtitle">Simple smart study planning</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Task",
            "My Tasks",
            "Study Plan",
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

    st.metric("Active tasks", active_count)
    st.metric("Urgent / overdue", urgent_count)

render_header()

if page == "Dashboard":
    dashboard_page(tasks, availability)
elif page == "Add Task":
    add_task_page()
elif page == "My Tasks":
    my_tasks_page(tasks)
else:
    study_plan_page(tasks, availability)