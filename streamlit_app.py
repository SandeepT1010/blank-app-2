from __future__ import annotations

import html
import json
import os
import re
import sqlite3
import time as time_module
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


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
# DARK / LIGHT THEME
# ---------------------------------------------------------

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Dark"


THEME_PALETTES = {
    "Dark": {
        "page": "#071416",
        "page_end": "#061113",
        "page_glow_1": "rgba(45, 212, 191, 0.11)",
        "page_glow_2": "rgba(20, 184, 166, 0.07)",
        "header": "rgba(7, 20, 22, 0.84)",
        "sidebar_start": "#0d282a",
        "sidebar": "#0b2023",
        "sidebar_end": "#08191b",
        "card": "#10272b",
        "card_alt": "#0d2226",
        "card_hover": "#153238",
        "input": "#0c2024",
        "text": "#f4fbfa",
        "text_soft": "#b8ccca",
        "text_faint": "#8fa9a7",
        "accent": "#2dd4bf",
        "accent_hover": "#5eead4",
        "accent_text": "#032421",
        "border": "rgba(144, 205, 200, 0.24)",
        "border_strong": "rgba(45, 212, 191, 0.48)",
        "shadow": "rgba(0, 0, 0, 0.30)",
        "nav_text": "#d9e9e7",
        "nav_hover": "#123438",
        "nav_selected_1": "#164b4d",
        "nav_selected_2": "#123b3f",
        "form": "rgba(13, 34, 38, 0.62)",
        "alert": "#10282c",
        "progress_track": "#173438",
        "table": "#0d2226",
    },
    "Light": {
        "page": "#edf5f3",
        "page_end": "#f8fbfa",
        "page_glow_1": "rgba(15, 118, 110, 0.12)",
        "page_glow_2": "rgba(20, 184, 166, 0.08)",
        "header": "rgba(248, 251, 250, 0.88)",
        "sidebar_start": "#dcece8",
        "sidebar": "#e8f3f0",
        "sidebar_end": "#f1f7f5",
        "card": "#ffffff",
        "card_alt": "#f3f8f6",
        "card_hover": "#edf7f4",
        "input": "#ffffff",
        "text": "#153a3d",
        "text_soft": "#4e696b",
        "text_faint": "#6a8183",
        "accent": "#0f766e",
        "accent_hover": "#115e59",
        "accent_text": "#ffffff",
        "border": "rgba(39, 91, 88, 0.22)",
        "border_strong": "rgba(15, 118, 110, 0.50)",
        "shadow": "rgba(23, 59, 63, 0.13)",
        "nav_text": "#244c4f",
        "nav_hover": "#d8ebe7",
        "nav_selected_1": "#c9e7e1",
        "nav_selected_2": "#d8eeea",
        "form": "rgba(255, 255, 255, 0.76)",
        "alert": "#e7f3f0",
        "progress_track": "#cfe3df",
        "table": "#ffffff",
    },
}


def apply_app_theme(theme_name: str) -> None:
    palette = THEME_PALETTES[theme_name]

    css = """
    <style>
        :root {
            --page: %%PAGE%%;
            --page-end: %%PAGE_END%%;
            --page-glow-1: %%PAGE_GLOW_1%%;
            --page-glow-2: %%PAGE_GLOW_2%%;
            --header: %%HEADER%%;
            --sidebar-start: %%SIDEBAR_START%%;
            --sidebar: %%SIDEBAR%%;
            --sidebar-end: %%SIDEBAR_END%%;
            --card: %%CARD%%;
            --card-alt: %%CARD_ALT%%;
            --card-hover: %%CARD_HOVER%%;
            --input: %%INPUT%%;
            --text: %%TEXT%%;
            --text-soft: %%TEXT_SOFT%%;
            --text-faint: %%TEXT_FAINT%%;
            --accent: %%ACCENT%%;
            --accent-hover: %%ACCENT_HOVER%%;
            --accent-text: %%ACCENT_TEXT%%;
            --border: %%BORDER%%;
            --border-strong: %%BORDER_STRONG%%;
            --shadow: %%SHADOW%%;
            --nav-text: %%NAV_TEXT%%;
            --nav-hover: %%NAV_HOVER%%;
            --nav-selected-1: %%NAV_SELECTED_1%%;
            --nav-selected-2: %%NAV_SELECTED_2%%;
            --form: %%FORM%%;
            --alert: %%ALERT%%;
            --progress-track: %%PROGRESS_TRACK%%;
            --table: %%TABLE%%;
        }

        html, body, [class*="css"] {
            color: var(--text);
        }

        .stApp,
        [data-testid="stAppViewContainer"] {
            color: var(--text);
            background:
                radial-gradient(circle at 12% 0%, var(--page-glow-1), transparent 28rem),
                radial-gradient(circle at 88% 5%, var(--page-glow-2), transparent 25rem),
                linear-gradient(180deg, var(--page) 0%, var(--page-end) 100%);
        }

        [data-testid="stHeader"] {
            background: var(--header);
        }

        .block-container {
            max-width: 1260px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stCaptionContainer"],
        label {
            color: var(--text);
        }

        [data-testid="stCaptionContainer"],
        .stCaption,
        small {
            color: var(--text-soft) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    var(--sidebar-start) 0%,
                    var(--sidebar) 42%,
                    var(--sidebar-end) 100%
                );
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] > div {
            background: transparent;
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .brand {
            padding: 1.08rem;
            border: 1px solid rgba(94, 234, 212, 0.34);
            border-radius: 18px;
            background: linear-gradient(135deg, #0f766e, #115e59);
            color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 12px 30px var(--shadow);
        }

        .brand-title {
            color: #ffffff;
            font-size: 1.38rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            color: #d7fffa;
            font-size: 0.82rem;
            opacity: 0.94;
            margin-top: 0.22rem;
        }

        .theme-label {
            color: var(--text-soft);
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.04em;
            margin: 0.2rem 0 0.35rem;
            text-transform: uppercase;
        }

        /* Clean sidebar navigation */
        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0.42rem;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            width: 100%;
            cursor: pointer;
            border: 1px solid transparent;
            border-radius: 12px;
            padding: 0.66rem 0.78rem;
            margin: 0;
            background: transparent;
            transition: 0.15s ease;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label p {
            color: var(--nav-text) !important;
            font-weight: 650;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background: var(--nav-hover);
            border-color: var(--border);
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
            background:
                linear-gradient(
                    135deg,
                    var(--nav-selected-1),
                    var(--nav-selected-2)
                );
            border-color: var(--accent);
            box-shadow: 0 6px 18px var(--shadow);
        }

        [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
            color: var(--text) !important;
        }

        /* Toggle */
        [data-testid="stToggle"] label p {
            color: var(--text) !important;
            font-weight: 700;
        }

        /* Main cards */
        .hero {
            padding: 1.35rem 1.45rem;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            margin-bottom: 1.2rem;
            box-shadow: 0 12px 30px var(--shadow);
        }

        .hero h1 {
            color: var(--text);
            font-size: 2rem;
            margin: 0;
            letter-spacing: -0.035em;
        }

        .hero p {
            color: var(--text-soft);
            margin: 0.45rem 0 0;
        }

        .task-card {
            padding: 0.95rem 1rem;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            margin-bottom: 0.68rem;
            box-shadow: 0 6px 18px var(--shadow);
        }

        .task-card:hover {
            background: var(--card-hover);
            border-color: var(--border-strong);
        }

        .urgent { border-left: 6px solid #ef5f5f; }
        .soon { border-left: 6px solid #eaa72e; }
        .normal { border-left: 6px solid #20a486; }
        .overdue { border-left: 6px solid #d93636; }

        .task-title {
            color: var(--text);
            font-weight: 760;
            font-size: 1rem;
        }

        .task-meta {
            color: var(--text-soft);
            font-size: 0.87rem;
            margin-top: 0.3rem;
        }

        .badge {
            display: inline-block;
            margin-top: 0.45rem;
            margin-right: 0.25rem;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 760;
            border: 1px solid transparent;
        }

        .red {
            color: #7f1d1d;
            background: #fee2e2;
            border-color: #fca5a5;
        }

        .orange {
            color: #78350f;
            background: #fef3c7;
            border-color: #fcd34d;
        }

        .green {
            color: #065f46;
            background: #d1fae5;
            border-color: #6ee7b7;
        }

        .teal {
            color: #115e59;
            background: #ccfbf1;
            border-color: #5eead4;
        }

        .gray {
            color: #334155;
            background: #e2e8f0;
            border-color: #cbd5e1;
        }

        .next-task {
            padding: 1.15rem;
            border: 1px solid rgba(94, 234, 212, 0.38);
            border-radius: 17px;
            color: #ffffff;
            background: linear-gradient(135deg, #0f766e, #115e59);
            box-shadow: 0 14px 30px var(--shadow);
        }

        .timer-card {
            text-align: center;
            padding: 1.55rem 1rem;
            border: 1px solid var(--border-strong);
            border-radius: 22px;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            box-shadow: 0 14px 34px var(--shadow);
            margin: 0.75rem 0;
        }

        .timer-task {
            color: var(--text-soft);
            font-size: 0.92rem;
            font-weight: 650;
        }

        .timer-display {
            color: var(--text);
            font-size: clamp(3.4rem, 9vw, 6rem);
            line-height: 1;
            font-weight: 850;
            letter-spacing: -0.06em;
            margin: 0.55rem 0;
            font-variant-numeric: tabular-nums;
        }

        .timer-status {
            color: var(--accent);
            font-size: 0.9rem;
            font-weight: 760;
        }

        .session-card {
            padding: 0.82rem 0.92rem;
            border-radius: 13px;
            color: var(--text);
            background: var(--card-alt);
            border: 1px solid var(--border);
            margin: 0.45rem 0;
        }

        .session-card strong {
            color: var(--text);
        }

        .session-card span {
            color: var(--text-soft) !important;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            padding: 0.9rem;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            box-shadow: 0 7px 20px var(--shadow);
        }

        [data-testid="stMetricLabel"] p {
            color: var(--text-soft) !important;
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            color: var(--text) !important;
        }

        [data-testid="stMetricDelta"] {
            color: var(--accent) !important;
        }

        /* Buttons */
        .stButton > button,
        .stDownloadButton > button {
            min-height: 2.65rem;
            border-radius: 11px;
            border: 1px solid var(--border-strong);
            color: var(--text);
            background: var(--card-alt);
            font-weight: 700;
            box-shadow: none;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            color: var(--text);
            background: var(--card-hover);
            border-color: var(--accent);
        }

        .stButton > button[kind="primary"] {
            color: var(--accent-text);
            background: var(--accent);
            border-color: var(--accent);
        }

        .stButton > button[kind="primary"]:hover {
            color: var(--accent-text);
            background: var(--accent-hover);
            border-color: var(--accent-hover);
        }

        .stButton > button:disabled {
            color: var(--text-faint) !important;
            background: var(--card-alt) !important;
            border-color: var(--border) !important;
            opacity: 0.72;
        }

        /* Inputs */
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stTimeInput label,
        .stSelectbox label,
        .stSlider label,
        .stCheckbox label,
        .stRadio label {
            color: var(--text) !important;
            font-weight: 650;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        [data-baseweb="input"] input {
            color: var(--text) !important;
            background: var(--input) !important;
            border-color: var(--border) !important;
            border-radius: 10px;
        }

        .stTextInput input::placeholder {
            color: var(--text-faint) !important;
        }

        div[data-baseweb="select"] > div {
            color: var(--text) !important;
            background: var(--input) !important;
            border-color: var(--border) !important;
            border-radius: 10px;
        }

        div[data-baseweb="select"] span {
            color: var(--text) !important;
        }

        [data-baseweb="popover"],
        [role="listbox"] {
            color: var(--text) !important;
            background: var(--card) !important;
        }

        [role="option"] {
            color: var(--text) !important;
            background: var(--card) !important;
        }

        [role="option"]:hover {
            background: var(--card-hover) !important;
        }

        /* Expanders, forms, tables */
        [data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 13px;
            background: var(--card-alt);
        }

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p {
            color: var(--text) !important;
        }

        [data-testid="stForm"] {
            border-color: var(--border);
            background: var(--form);
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 13px;
            overflow: hidden;
            background: var(--table);
        }

        /* Alerts */
        [data-testid="stAlert"] {
            color: var(--text);
            border: 1px solid var(--border);
            background: var(--alert);
        }

        [data-testid="stAlert"] p {
            color: var(--text) !important;
        }

        /* Progress bars */
        [data-testid="stProgress"] > div > div {
            background: var(--progress-track);
        }

        [data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, #14b8a6, #5eead4);
        }

        hr {
            border-color: var(--border);
        }

        .session-card span,
        .task-card span {
            text-rendering: optimizeLegibility;
        }
    </style>
    """

    replacements = {
        "%%PAGE%%": palette["page"],
        "%%PAGE_END%%": palette["page_end"],
        "%%PAGE_GLOW_1%%": palette["page_glow_1"],
        "%%PAGE_GLOW_2%%": palette["page_glow_2"],
        "%%HEADER%%": palette["header"],
        "%%SIDEBAR_START%%": palette["sidebar_start"],
        "%%SIDEBAR%%": palette["sidebar"],
        "%%SIDEBAR_END%%": palette["sidebar_end"],
        "%%CARD%%": palette["card"],
        "%%CARD_ALT%%": palette["card_alt"],
        "%%CARD_HOVER%%": palette["card_hover"],
        "%%INPUT%%": palette["input"],
        "%%TEXT%%": palette["text"],
        "%%TEXT_SOFT%%": palette["text_soft"],
        "%%TEXT_FAINT%%": palette["text_faint"],
        "%%ACCENT%%": palette["accent"],
        "%%ACCENT_HOVER%%": palette["accent_hover"],
        "%%ACCENT_TEXT%%": palette["accent_text"],
        "%%BORDER%%": palette["border"],
        "%%BORDER_STRONG%%": palette["border_strong"],
        "%%SHADOW%%": palette["shadow"],
        "%%NAV_TEXT%%": palette["nav_text"],
        "%%NAV_HOVER%%": palette["nav_hover"],
        "%%NAV_SELECTED_1%%": palette["nav_selected_1"],
        "%%NAV_SELECTED_2%%": palette["nav_selected_2"],
        "%%FORM%%": palette["form"],
        "%%ALERT%%": palette["alert"],
        "%%PROGRESS_TRACK%%": palette["progress_track"],
        "%%TABLE%%": palette["table"],
    }

    for token, value in replacements.items():
        css = css.replace(token, value)

    st.markdown(css, unsafe_allow_html=True)


apply_app_theme(st.session_state.app_theme)

st.markdown(
    """
    <style>
        .resource-card,
        .video-card,
        .tool-card {
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            box-shadow: 0 7px 20px var(--shadow);
            margin-bottom: 0.75rem;
        }

        .resource-card h4,
        .video-card h4,
        .tool-card h4 {
            color: var(--text);
            margin: 0 0 0.35rem;
        }

        .resource-description,
        .video-description,
        .tool-description {
            color: var(--text-soft);
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .video-thumbnail {
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow: hidden;
        }

        .section-eyebrow {
            color: var(--accent);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }

        .api-help {
            padding: 0.85rem 0.95rem;
            border-radius: 13px;
            border: 1px solid var(--border);
            background: var(--card-alt);
            color: var(--text-soft);
            margin-bottom: 0.8rem;
        }

        .api-help strong {
            color: var(--text);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        .youtube-shell {
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1rem;
            background: linear-gradient(145deg, var(--card), var(--card-alt));
            box-shadow: 0 14px 34px var(--shadow);
            margin-bottom: 1rem;
        }

        .youtube-brand-row {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin-bottom: 0.9rem;
        }

        .youtube-play-mark {
            width: 2.2rem;
            height: 1.55rem;
            border-radius: 0.48rem;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            color: white;
            background: #ff0033;
            font-size: 0.82rem;
            font-weight: 900;
            box-shadow: 0 6px 18px rgba(255, 0, 51, 0.24);
        }

        .youtube-watcher-title {
            color: var(--text);
            font-size: 1.35rem;
            font-weight: 850;
            letter-spacing: -0.03em;
        }

        .youtube-watcher-subtitle {
            color: var(--text-soft);
            font-size: 0.86rem;
        }

        .youtube-result-card {
            min-height: 100%;
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 0.75rem;
            background: var(--card-alt);
            box-shadow: 0 6px 18px var(--shadow);
            margin-bottom: 0.65rem;
        }

        .youtube-result-title {
            color: var(--text);
            font-size: 0.98rem;
            line-height: 1.3;
            font-weight: 780;
            margin-top: 0.55rem;
        }

        .youtube-result-meta {
            color: var(--text-soft);
            font-size: 0.82rem;
            line-height: 1.4;
            margin-top: 0.35rem;
        }

        .youtube-filter-label {
            color: var(--text-soft);
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }

        .youtube-player-box {
            border: 1px solid var(--border-strong);
            border-radius: 18px;
            padding: 0.9rem;
            background: var(--card-alt);
            margin: 0.9rem 0 1.1rem;
        }

        .youtube-player-title {
            color: var(--text);
            font-size: 1.08rem;
            font-weight: 780;
            margin-bottom: 0.15rem;
        }

        .youtube-player-meta {
            color: var(--text-soft);
            font-size: 0.84rem;
            margin-bottom: 0.7rem;
        }

        .youtube-empty {
            text-align: center;
            padding: 2.5rem 1rem;
            border: 1px dashed var(--border-strong);
            border-radius: 17px;
            color: var(--text-soft);
            background: var(--card-alt);
        }

        .youtube-search-help {
            color: var(--text-soft);
            font-size: 0.82rem;
            margin-top: -0.25rem;
            margin-bottom: 0.75rem;
        }

        .youtube-shell [data-testid="stForm"] {
            border: 0;
            padding: 0;
            background: transparent;
        }

        .youtube-shell .stTextInput input {
            min-height: 3rem;
            font-size: 1rem;
            border-radius: 999px;
            padding-left: 1.15rem;
        }

        .youtube-shell .stButton > button,
        .youtube-shell .stFormSubmitButton > button {
            border-radius: 999px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        .shorts-note {
            padding: 0.75rem 0.9rem;
            border: 1px solid var(--border);
            border-radius: 13px;
            color: var(--text-soft);
            background: var(--card-alt);
            margin-bottom: 0.75rem;
        }

        .video-type-badge {
            display: inline-block;
            padding: 0.18rem 0.48rem;
            border-radius: 999px;
            color: var(--text);
            background: var(--card-hover);
            border: 1px solid var(--border);
            font-size: 0.72rem;
            font-weight: 760;
            margin-top: 0.35rem;
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
                study_hours REAL NOT NULL,
                start_time TEXT NOT NULL DEFAULT '16:00',
                end_time TEXT NOT NULL DEFAULT '18:00'
            )
            """
        )

        availability_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(availability)"
            ).fetchall()
        }

        added_time_columns = False

        if "start_time" not in availability_columns:
            connection.execute(
                """
                ALTER TABLE availability
                ADD COLUMN start_time TEXT NOT NULL DEFAULT '16:00'
                """
            )
            added_time_columns = True

        if "end_time" not in availability_columns:
            connection.execute(
                """
                ALTER TABLE availability
                ADD COLUMN end_time TEXT NOT NULL DEFAULT '18:00'
                """
            )
            added_time_columns = True

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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS youtube_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                channel_reference TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS study_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                resource_url TEXT NOT NULL,
                category TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )

        for day_name in DAYS:
            is_weekend = day_name in {"Saturday", "Sunday"}
            default_hours = 3.0 if is_weekend else 2.0
            default_start = "10:00" if is_weekend else "16:00"
            default_end = "13:00" if is_weekend else "18:00"

            connection.execute(
                """
                INSERT OR IGNORE INTO availability (
                    day_name,
                    study_hours,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    day_name,
                    default_hours,
                    default_start,
                    default_end,
                ),
            )

        # Preserve hours from an older StudyFlow database by converting them
        # into a matching start/end window the first time this version runs.
        if added_time_columns:
            rows = connection.execute(
                """
                SELECT day_name, study_hours
                FROM availability
                """
            ).fetchall()

            for row in rows:
                is_weekend = row["day_name"] in {"Saturday", "Sunday"}
                start_value = time(10, 0) if is_weekend else time(16, 0)
                start_dt = datetime.combine(date.today(), start_value)
                end_dt = start_dt + timedelta(
                    hours=max(0.0, float(row["study_hours"]))
                )

                connection.execute(
                    """
                    UPDATE availability
                    SET start_time = ?, end_time = ?
                    WHERE day_name = ?
                    """,
                    (
                        start_value.strftime("%H:%M"),
                        end_dt.time().strftime("%H:%M"),
                        row["day_name"],
                    ),
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


def availability_window_hours(day_settings: dict) -> float:
    if not day_settings.get("enabled", False):
        return 0.0

    start_value = time.fromisoformat(day_settings["start"])
    end_value = time.fromisoformat(day_settings["end"])

    start_dt = datetime.combine(date.today(), start_value)
    end_dt = datetime.combine(date.today(), end_value)

    return max(0.0, (end_dt - start_dt).total_seconds() / 3600)


def get_availability() -> dict[str, dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT day_name, study_hours, start_time, end_time
            FROM availability
            """
        ).fetchall()

    saved = {
        row["day_name"]: {
            "enabled": float(row["study_hours"]) > 0,
            "start": row["start_time"],
            "end": row["end_time"],
        }
        for row in rows
    }

    result: dict[str, dict] = {}

    for day_name in DAYS:
        is_weekend = day_name in {"Saturday", "Sunday"}
        result[day_name] = saved.get(
            day_name,
            {
                "enabled": True,
                "start": "10:00" if is_weekend else "16:00",
                "end": "13:00" if is_weekend else "18:00",
            },
        )

    return result



def save_availability(availability: dict[str, dict]) -> None:
    with connect() as connection:
        for day_name, values in availability.items():
            enabled = bool(values["enabled"])
            start_value = time.fromisoformat(values["start"])
            end_value = time.fromisoformat(values["end"])

            if enabled:
                start_dt = datetime.combine(date.today(), start_value)
                end_dt = datetime.combine(date.today(), end_value)
                study_hours = max(
                    0.0,
                    (end_dt - start_dt).total_seconds() / 3600,
                )
            else:
                study_hours = 0.0

            connection.execute(
                """
                INSERT INTO availability (
                    day_name,
                    study_hours,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(day_name)
                DO UPDATE SET
                    study_hours = excluded.study_hours,
                    start_time = excluded.start_time,
                    end_time = excluded.end_time
                """,
                (
                    day_name,
                    study_hours,
                    values["start"],
                    values["end"],
                ),
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
# ADDITIONAL RESOURCES FUNCTIONS
# ---------------------------------------------------------

def normalize_youtube_channel_reference(reference: str) -> str | None:
    value = reference.strip().rstrip("/")

    if not value:
        return None

    if "youtube.com" in value:
        parsed = urllib.parse.urlparse(
            value if "://" in value else f"https://{value}"
        )
        path_parts = [
            part for part in parsed.path.split("/") if part
        ]

        if not path_parts:
            return None

        if path_parts[0].startswith("@"):
            return path_parts[0]

        if (
            path_parts[0] == "channel"
            and len(path_parts) >= 2
        ):
            return path_parts[1]

        return None

    if value.startswith("@"):
        return value

    if value.startswith("UC") and len(value) >= 20:
        return value

    if " " not in value:
        return f"@{value.lstrip('@')}"

    return None


def add_youtube_channel(
    channel_name: str,
    channel_reference: str,
) -> tuple[bool, str]:
    normalized = normalize_youtube_channel_reference(
        channel_reference
    )

    if not normalized:
        return (
            False,
            "Use an @handle, a channel URL, or a channel ID beginning with UC.",
        )

    try:
        with connect() as connection:
            connection.execute(
                """
                INSERT INTO youtube_channels (
                    channel_name,
                    channel_reference,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    channel_name.strip(),
                    normalized,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
    except sqlite3.IntegrityError:
        return False, "That YouTube channel is already saved."

    return True, "YouTube channel added."


def get_youtube_channels() -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM youtube_channels
            ORDER BY channel_name COLLATE NOCASE
            """
        ).fetchall()

    return [dict(row) for row in rows]


def delete_youtube_channel(channel_id: int) -> None:
    with connect() as connection:
        connection.execute(
            "DELETE FROM youtube_channels WHERE id = ?",
            (channel_id,),
        )


def add_study_resource(
    title: str,
    resource_url: str,
    category: str,
    notes: str,
) -> tuple[bool, str]:
    clean_url = resource_url.strip()

    if not clean_url.startswith(("https://", "http://")):
        return False, "The resource URL must begin with https:// or http://."

    with connect() as connection:
        connection.execute(
            """
            INSERT INTO study_resources (
                title,
                resource_url,
                category,
                notes,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                clean_url,
                category,
                notes.strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    return True, "Resource saved."


def get_study_resources() -> list[dict]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM study_resources
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def delete_study_resource(resource_id: int) -> None:
    with connect() as connection:
        connection.execute(
            "DELETE FROM study_resources WHERE id = ?",
            (resource_id,),
        )


def get_default_youtube_api_key() -> str:
    environment_key = os.getenv("YOUTUBE_API_KEY", "").strip()

    if environment_key:
        return environment_key

    try:
        secret_key = str(
            st.secrets.get("YOUTUBE_API_KEY", "")
        ).strip()
    except Exception:
        secret_key = ""

    return secret_key


def youtube_api_request(
    endpoint: str,
    parameters: dict,
    api_key: str,
) -> dict:
    request_parameters = dict(parameters)
    request_parameters["key"] = api_key

    query_string = urllib.parse.urlencode(
        request_parameters,
        doseq=True,
    )
    request_url = (
        f"https://www.googleapis.com/youtube/v3/{endpoint}"
        f"?{query_string}"
    )

    request = urllib.request.Request(
        request_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "StudyFlow/1.0",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=12,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )
    except urllib.error.HTTPError as error:
        try:
            error_payload = json.loads(
                error.read().decode("utf-8")
            )
            message = (
                error_payload.get("error", {})
                .get("message", "YouTube API request failed.")
            )
        except Exception:
            message = "YouTube API request failed."

        raise RuntimeError(message) from error
    except urllib.error.URLError as error:
        raise RuntimeError(
            "Could not connect to YouTube. Check your internet connection."
        ) from error


def resolve_youtube_channel(
    channel: dict,
    api_key: str,
) -> dict:
    reference = channel["channel_reference"]

    parameters = {
        "part": "snippet,contentDetails",
        "maxResults": 1,
    }

    if reference.startswith("UC"):
        parameters["id"] = reference
    else:
        parameters["forHandle"] = reference

    payload = youtube_api_request(
        "channels",
        parameters,
        api_key,
    )
    items = payload.get("items", [])

    if not items:
        raise RuntimeError(
            f"No YouTube channel was found for {reference}."
        )

    item = items[0]
    uploads_playlist = (
        item.get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
    )

    if not uploads_playlist:
        raise RuntimeError(
            f"The uploads playlist for {reference} could not be found."
        )

    return {
        "saved_id": channel["id"],
        "display_name": channel["channel_name"],
        "official_name": (
            item.get("snippet", {}).get("title")
            or channel["channel_name"]
        ),
        "uploads_playlist": uploads_playlist,
    }


def get_recent_youtube_videos(
    channels: list[dict],
    api_key: str,
    videos_per_channel: int,
) -> tuple[list[dict], list[str]]:
    videos: list[dict] = []
    errors: list[str] = []

    for channel in channels:
        try:
            resolved = resolve_youtube_channel(
                channel,
                api_key,
            )

            payload = youtube_api_request(
                "playlistItems",
                {
                    "part": "snippet,contentDetails",
                    "playlistId": resolved["uploads_playlist"],
                    "maxResults": videos_per_channel,
                },
                api_key,
            )

            for item in payload.get("items", []):
                snippet = item.get("snippet", {})
                video_id = (
                    item.get("contentDetails", {}).get("videoId")
                    or snippet.get("resourceId", {}).get("videoId")
                )

                title = snippet.get("title", "").strip()

                if (
                    not video_id
                    or not title
                    or title in {"Private video", "Deleted video"}
                ):
                    continue

                thumbnails = snippet.get("thumbnails", {})
                thumbnail_url = ""

                for size in ("high", "medium", "default"):
                    if thumbnails.get(size, {}).get("url"):
                        thumbnail_url = thumbnails[size]["url"]
                        break

                videos.append(
                    {
                        "video_id": video_id,
                        "title": title,
                        "channel": (
                            snippet.get("videoOwnerChannelTitle")
                            or resolved["official_name"]
                        ),
                        "published_at": snippet.get(
                            "publishedAt",
                            "",
                        ),
                        "description": snippet.get(
                            "description",
                            "",
                        ),
                        "thumbnail": thumbnail_url,
                        "url": (
                            "https://www.youtube.com/watch"
                            f"?v={video_id}"
                        ),
                    }
                )

        except RuntimeError as error:
            errors.append(
                f"{channel['channel_name']}: {error}"
            )

    videos.sort(
        key=lambda video: video["published_at"],
        reverse=True,
    )

    return videos, errors


def resolve_youtube_channel_search(
    query: str,
    api_key: str,
) -> tuple[str, str]:
    clean_query = query.strip()

    if clean_query.startswith("UC") and len(clean_query) >= 20:
        payload = youtube_api_request(
            "channels",
            {
                "part": "snippet",
                "id": clean_query,
                "maxResults": 1,
            },
            api_key,
        )
    elif clean_query.startswith("@"):
        payload = youtube_api_request(
            "channels",
            {
                "part": "snippet",
                "forHandle": clean_query,
                "maxResults": 1,
            },
            api_key,
        )
    else:
        search_payload = youtube_api_request(
            "search",
            {
                "part": "snippet",
                "type": "channel",
                "q": clean_query,
                "maxResults": 1,
            },
            api_key,
        )
        channel_items = search_payload.get("items", [])

        if not channel_items:
            raise RuntimeError(
                f'No YouTube channel was found for "{clean_query}".'
            )

        channel_id = channel_items[0].get("id", {}).get("channelId", "")

        if not channel_id:
            raise RuntimeError(
                f'No YouTube channel was found for "{clean_query}".'
            )

        payload = youtube_api_request(
            "channels",
            {
                "part": "snippet",
                "id": channel_id,
                "maxResults": 1,
            },
            api_key,
        )

    items = payload.get("items", [])

    if not items:
        raise RuntimeError(
            f'No YouTube channel was found for "{clean_query}".'
        )

    channel = items[0]
    channel_id = channel.get("id", "")
    channel_title = (
        channel.get("snippet", {}).get("title")
        or clean_query
    )

    if not channel_id:
        raise RuntimeError(
            f'No YouTube channel was found for "{clean_query}".'
        )

    return channel_id, channel_title


def parse_youtube_duration(duration: str) -> int:
    """Convert an ISO 8601 YouTube duration to seconds."""
    pattern = re.compile(
        r"^P"
        r"(?:(?P<days>\d+)D)?"
        r"(?:T"
        r"(?:(?P<hours>\d+)H)?"
        r"(?:(?P<minutes>\d+)M)?"
        r"(?:(?P<seconds>\d+)S)?"
        r")?$"
    )
    match = pattern.match(duration or "")

    if not match:
        return 0

    values = {
        key: int(value or 0)
        for key, value in match.groupdict().items()
    }

    return (
        values["days"] * 86400
        + values["hours"] * 3600
        + values["minutes"] * 60
        + values["seconds"]
    )


def format_video_duration(seconds: int) -> str:
    if seconds <= 0:
        return "Duration unavailable"

    hours, remainder = divmod(seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"

    return f"{minutes}:{remaining_seconds:02d}"


def add_youtube_durations(
    videos: list[dict],
    api_key: str,
) -> list[dict]:
    video_ids = [
        video["video_id"]
        for video in videos
        if video.get("video_id")
    ]

    if not video_ids:
        return videos

    payload = youtube_api_request(
        "videos",
        {
            "part": "contentDetails",
            "id": ",".join(video_ids),
        },
        api_key,
    )

    duration_lookup: dict[str, int] = {}

    for item in payload.get("items", []):
        video_id = item.get("id", "")
        duration_text = (
            item.get("contentDetails", {}).get("duration", "")
        )
        duration_lookup[video_id] = parse_youtube_duration(
            duration_text
        )

    enriched: list[dict] = []

    for video in videos:
        duration_seconds = duration_lookup.get(
            video["video_id"],
            0,
        )
        updated = video.copy()
        updated["duration_seconds"] = duration_seconds
        updated["duration_text"] = format_video_duration(
            duration_seconds
        )
        updated["video_type"] = (
            "Short"
            if 0 < duration_seconds <= 180
            else "Video"
        )
        enriched.append(updated)

    return enriched


def render_shorts_scroll_feed(
    videos: list[dict],
    theme_name: str,
) -> None:
    if not videos:
        return

    is_dark = theme_name == "Dark"
    background = "#071416" if is_dark else "#edf5f3"
    card = "#10272b" if is_dark else "#ffffff"
    text = "#f4fbfa" if is_dark else "#153a3d"
    soft_text = "#b8ccca" if is_dark else "#4e696b"
    border = (
        "rgba(144,205,200,0.28)"
        if is_dark
        else "rgba(39,91,88,0.24)"
    )
    button_background = "#0f766e"
    button_text = "#ffffff"

    short_sections: list[str] = []

    for index, video in enumerate(videos):
        video_id = html.escape(video["video_id"])
        title = html.escape(video["title"])
        channel = html.escape(video["channel"])
        date_text = html.escape(
            format_youtube_date(video["published_at"])
        )

        short_sections.append(
            f"""
            <section class="short-card" data-short-index="{index}">
                <div class="phone-frame">
                    <iframe
                        class="short-player"
                        src="https://www.youtube.com/embed/{video_id}?enablejsapi=1&playsinline=1&rel=0"
                        title="{title}"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen>
                    </iframe>
                </div>
                <div class="short-info">
                    <div class="short-title">{title}</div>
                    <div class="short-meta">{channel} · {date_text}</div>
                </div>
            </section>
            """
        )

    feed_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                color: {text};
                background: {background};
                font-family: Arial, Helvetica, sans-serif;
                overflow: hidden;
            }}

            .watcher {{
                position: relative;
                max-width: 620px;
                margin: 0 auto;
                padding: 0 4.5rem;
            }}

            .shorts-feed {{
                height: 720px;
                overflow-y: auto;
                scroll-snap-type: y mandatory;
                scrollbar-width: thin;
                border: 1px solid {border};
                border-radius: 20px;
                background: {card};
                box-shadow: 0 16px 38px rgba(0,0,0,0.22);
            }}

            .short-card {{
                min-height: 718px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                scroll-snap-align: start;
                scroll-snap-stop: always;
                padding: 1rem;
                border-bottom: 1px solid {border};
            }}

            .phone-frame {{
                width: min(100%, 365px);
                aspect-ratio: 9 / 16;
                overflow: hidden;
                border: 1px solid {border};
                border-radius: 22px;
                background: #000000;
                box-shadow: 0 12px 28px rgba(0,0,0,0.26);
            }}

            .short-player {{
                width: 100%;
                height: 100%;
            }}

            .short-info {{
                width: min(100%, 365px);
                padding: 0.8rem 0.25rem 0;
            }}

            .short-title {{
                color: {text};
                font-size: 1rem;
                font-weight: 750;
                line-height: 1.35;
            }}

            .short-meta {{
                color: {soft_text};
                font-size: 0.82rem;
                margin-top: 0.32rem;
            }}

            .nav-button {{
                position: absolute;
                right: 0.3rem;
                width: 3rem;
                height: 3rem;
                border: 0;
                border-radius: 999px;
                color: {button_text};
                background: {button_background};
                font-size: 1.15rem;
                font-weight: 800;
                cursor: pointer;
                box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            }}

            .nav-button:hover {{
                transform: scale(1.04);
            }}

            .previous {{
                top: calc(50% - 3.6rem);
            }}

            .next {{
                top: calc(50% + 0.6rem);
            }}

            .counter {{
                position: absolute;
                left: 0;
                top: 0.9rem;
                padding: 0.4rem 0.55rem;
                color: {soft_text};
                background: {card};
                border: 1px solid {border};
                border-radius: 999px;
                font-size: 0.76rem;
                font-weight: 700;
            }}

            @media (max-width: 560px) {{
                .watcher {{
                    padding: 0 3.6rem 0 0;
                }}

                .counter {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="watcher">
            <div class="counter" id="shortCounter">1 / {len(videos)}</div>
            <div class="shorts-feed" id="shortsFeed">
                {''.join(short_sections)}
            </div>
            <button class="nav-button previous"
                    onclick="moveShort(-1)"
                    aria-label="Previous Short">↑</button>
            <button class="nav-button next"
                    onclick="moveShort(1)"
                    aria-label="Next Short">↓</button>
        </div>

        <script>
            const feed = document.getElementById("shortsFeed");
            const cards = Array.from(
                feed.querySelectorAll(".short-card")
            );
            const counter = document.getElementById("shortCounter");
            let currentIndex = 0;

            function pauseAllExcept(activeIndex) {{
                cards.forEach((card, index) => {{
                    if (index === activeIndex) return;
                    const player = card.querySelector("iframe");
                    if (player && player.contentWindow) {{
                        player.contentWindow.postMessage(
                            JSON.stringify({{
                                event: "command",
                                func: "pauseVideo",
                                args: []
                            }}),
                            "*"
                        );
                    }}
                }});
            }}

            function updateCounter(index) {{
                currentIndex = Math.max(
                    0,
                    Math.min(cards.length - 1, index)
                );
                counter.textContent =
                    `${{currentIndex + 1}} / ${{cards.length}}`;
                pauseAllExcept(currentIndex);
            }}

            function moveShort(direction) {{
                const targetIndex = Math.max(
                    0,
                    Math.min(
                        cards.length - 1,
                        currentIndex + direction
                    )
                );

                cards[targetIndex].scrollIntoView({{
                    behavior: "smooth",
                    block: "start"
                }});
                updateCounter(targetIndex);
            }}

            const observer = new IntersectionObserver(
                entries => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting
                            && entry.intersectionRatio >= 0.65) {{
                            const index = Number(
                                entry.target.dataset.shortIndex
                            );
                            updateCounter(index);
                        }}
                    }});
                }},
                {{
                    root: feed,
                    threshold: [0.65]
                }}
            );

            cards.forEach(card => observer.observe(card));

            feed.addEventListener("keydown", event => {{
                if (event.key === "ArrowDown") moveShort(1);
                if (event.key === "ArrowUp") moveShort(-1);
            }});

            feed.tabIndex = 0;
        </script>
    </body>
    </html>
    """

    components.html(
        feed_html,
        height=760,
        scrolling=False,
    )

def search_youtube_watcher(
    query: str,
    api_key: str,
    search_mode: str,
    sort_order: str,
    video_type: str,
    page_token: str = "",
    max_results: int = 12,
) -> tuple[list[dict], str, int, str]:
    clean_query = query.strip()

    if not clean_query:
        raise RuntimeError("Enter a channel or topic to search.")

    request_size = (
        max_results
        if video_type == "Everything"
        else min(50, max_results * 3)
    )

    parameters = {
        "part": "snippet",
        "type": "video",
        "maxResults": request_size,
        "safeSearch": "moderate",
        "videoEmbeddable": "true",
        "videoSyndicated": "true",
        "order": (
            "date"
            if sort_order == "Newest"
            else "viewCount"
            if sort_order == "Most viewed"
            else "relevance"
        ),
    }

    # YouTube's API "short" duration category is under four minutes.
    # Exact duration metadata is checked again after the search so this
    # app can use the current three-minute Shorts limit.
    if video_type == "Shorts":
        parameters["videoDuration"] = "short"

    resolved_label = clean_query

    if search_mode == "Channel":
        channel_id, channel_title = resolve_youtube_channel_search(
            clean_query,
            api_key,
        )
        parameters["channelId"] = channel_id
        resolved_label = channel_title

        if sort_order == "Relevant":
            parameters["order"] = "date"
    else:
        parameters["q"] = clean_query

    if page_token:
        parameters["pageToken"] = page_token

    payload = youtube_api_request(
        "search",
        parameters,
        api_key,
    )

    raw_videos: list[dict] = []

    for item in payload.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})

        if not video_id:
            continue

        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = ""

        for size in ("high", "medium", "default"):
            candidate = thumbnails.get(size, {}).get("url")
            if candidate:
                thumbnail_url = candidate
                break

        raw_videos.append(
            {
                "video_id": video_id,
                "title": html.unescape(
                    snippet.get("title", "Untitled video")
                ),
                "channel": html.unescape(
                    snippet.get("channelTitle", "Unknown channel")
                ),
                "published_at": snippet.get("publishedAt", ""),
                "description": html.unescape(
                    snippet.get("description", "")
                ),
                "thumbnail": thumbnail_url,
                "url": (
                    "https://www.youtube.com/watch"
                    f"?v={video_id}"
                ),
            }
        )

    enriched_videos = add_youtube_durations(
        raw_videos,
        api_key,
    )

    if video_type == "Shorts":
        videos = [
            video
            for video in enriched_videos
            if video["video_type"] == "Short"
        ]
    elif video_type == "Videos":
        videos = [
            video
            for video in enriched_videos
            if video["video_type"] == "Video"
        ]
    else:
        videos = enriched_videos

    videos = videos[:max_results]

    next_page_token = payload.get("nextPageToken", "")
    total_results = int(
        payload.get("pageInfo", {}).get("totalResults", 0)
    )

    return (
        videos,
        next_page_token,
        total_results,
        resolved_label,
    )


def format_youtube_date(published_at: str) -> str:
    if not published_at:
        return "Publication date unavailable"

    try:
        published = datetime.fromisoformat(
            published_at.replace("Z", "+00:00")
        )
        now = datetime.now(published.tzinfo)
        difference = now - published

        if difference.days == 0:
            hours = max(1, difference.seconds // 3600)
            return f"{hours} hour(s) ago"

        if difference.days == 1:
            return "Yesterday"

        if difference.days < 30:
            return f"{difference.days} days ago"

        return published.strftime("%b %d, %Y")
    except ValueError:
        return published_at


def shorten_text(value: str, maximum: int = 180) -> str:
    cleaned = " ".join(value.split())

    if len(cleaned) <= maximum:
        return cleaned

    return cleaned[: maximum - 1].rstrip() + "…"

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
    availability: dict[str, dict],
) -> tuple[list[dict], list[str]]:
    today = date.today()
    now = datetime.now()
    plan_dates = [today + timedelta(days=offset) for offset in range(7)]

    day_windows: dict[date, dict] = {}

    for plan_date in plan_dates:
        weekday = plan_date.strftime("%A")
        settings = availability[weekday]

        if not settings["enabled"]:
            continue

        start_value = time.fromisoformat(settings["start"])
        end_value = time.fromisoformat(settings["end"])
        start_dt = datetime.combine(plan_date, start_value)
        end_dt = datetime.combine(plan_date, end_value)

        # Do not create sessions in the past for the current day.
        if plan_date == today and start_dt < now:
            minute = ((now.minute + 14) // 15) * 15
            rounded = now.replace(second=0, microsecond=0)

            if minute >= 60:
                rounded = rounded.replace(minute=0) + timedelta(hours=1)
            else:
                rounded = rounded.replace(minute=minute)

            start_dt = max(start_dt, rounded)

        if end_dt > start_dt:
            day_windows[plan_date] = {
                "next_start": start_dt,
                "end": end_dt,
            }

    active_tasks = [
        task.copy()
        for task in tasks
        if not task["completed"] and remaining_task_hours(task) > 0
    ]

    for task in active_tasks:
        task["remaining_minutes"] = int(
            round(remaining_task_hours(task) * 60)
        )
        task["score"] = smart_score(task)

    active_tasks.sort(
        key=lambda task: (-task["score"], task["due_date"])
    )

    schedule: list[dict] = []
    warnings: list[str] = []

    for task in active_tasks:
        due_date_value = date.fromisoformat(task["due_date"])

        if due_date_value < today:
            allowed_dates = list(day_windows.keys())
        else:
            allowed_dates = [
                plan_date
                for plan_date in day_windows
                if plan_date <= due_date_value
            ]

        while task["remaining_minutes"] > 0:
            possible_dates = []

            for plan_date in allowed_dates:
                window = day_windows[plan_date]
                free_minutes = int(
                    (window["end"] - window["next_start"]).total_seconds()
                    // 60
                )

                if free_minutes >= 15:
                    possible_dates.append(plan_date)

            if not possible_dates:
                break

            chosen_date = possible_dates[0]
            window = day_windows[chosen_date]
            free_minutes = int(
                (window["end"] - window["next_start"]).total_seconds() // 60
            )

            session_minutes = min(
                60,
                task["remaining_minutes"],
                free_minutes,
            )

            if session_minutes < 15 and task["remaining_minutes"] >= 15:
                window["next_start"] = window["end"]
                continue

            start_dt = window["next_start"]
            end_dt = start_dt + timedelta(minutes=session_minutes)

            schedule.append(
                {
                    "Date": chosen_date,
                    "Day": chosen_date.strftime("%A"),
                    "Time": (
                        f"{start_dt.strftime('%I:%M %p').lstrip('0')}"
                        f"–{end_dt.strftime('%I:%M %p').lstrip('0')}"
                    ),
                    "Subject": task["subject"],
                    "Task": task["task_name"],
                    "Study Time": (
                        f"{session_minutes / 60:.1f} hr"
                        if session_minutes >= 30
                        else f"{session_minutes} min"
                    ),
                    "Priority": task["priority"],
                    "Status": urgency(task)[0],
                    "_start": start_dt,
                }
            )

            task["remaining_minutes"] -= session_minutes

            # A short transition break keeps the generated timetable realistic.
            next_start = end_dt + timedelta(minutes=10)
            window["next_start"] = min(next_start, window["end"])

        if task["remaining_minutes"] > 0:
            warnings.append(
                f"{task['subject']} — {task['task_name']} still needs "
                f"{task['remaining_minutes'] / 60:.1f} hour(s)."
            )

    schedule.sort(key=lambda row: (row["Date"], row["_start"]))

    for row in schedule:
        row.pop("_start", None)

    return schedule, warnings



# ---------------------------------------------------------
# TIMER STATE AND LIVE TIMER
# ---------------------------------------------------------

def initialize_timer_state() -> None:
    defaults = {
        "timer_running": False,
        "timer_end_timestamp": 0.0,
        "timer_remaining_seconds": 25 * 60,
        "timer_focus_minutes": 25,
        "timer_break_minutes": 5,
        "timer_phase": "Focus",
        "timer_task_id": None,
        "timer_config": None,
        "timer_logged": False,
        "timer_complete_notice": False,
        "timer_break_complete_notice": False,
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

    if remaining_seconds <= 0 and st.session_state.timer_running:
        if st.session_state.timer_phase == "Focus":
            if (
                not st.session_state.timer_logged
                and st.session_state.timer_task_id is not None
            ):
                record_focus_session(
                    int(st.session_state.timer_task_id),
                    int(st.session_state.timer_focus_minutes),
                )
                st.session_state.timer_logged = True

            st.session_state.timer_complete_notice = True
            st.session_state.timer_break_complete_notice = False
            st.session_state.timer_phase = "Break"
            st.session_state.timer_remaining_seconds = (
                int(st.session_state.timer_break_minutes) * 60
            )
            st.session_state.timer_end_timestamp = (
                time_module.time()
                + st.session_state.timer_remaining_seconds
            )
            st.session_state.timer_running = True
            remaining_seconds = st.session_state.timer_remaining_seconds

        else:
            st.session_state.timer_running = False
            st.session_state.timer_phase = "Focus"
            st.session_state.timer_remaining_seconds = (
                int(st.session_state.timer_focus_minutes) * 60
            )
            st.session_state.timer_logged = False
            st.session_state.timer_break_complete_notice = True
            remaining_seconds = st.session_state.timer_remaining_seconds

    phase = st.session_state.timer_phase

    if phase == "Break":
        total_seconds = max(
            1,
            int(st.session_state.timer_break_minutes) * 60,
        )
    else:
        total_seconds = max(
            1,
            int(st.session_state.timer_focus_minutes) * 60,
        )

    progress = 1 - remaining_seconds / total_seconds
    progress = min(1.0, max(0.0, progress))

    minutes, seconds = divmod(remaining_seconds, 60)
    selected_task = (
        get_task(int(st.session_state.timer_task_id))
        if st.session_state.timer_task_id is not None
        else None
    )

    if phase == "Break":
        task_text = (
            f"Break · "
            f"{int(st.session_state.timer_break_minutes)} minutes"
        )
        status_text = (
            "Break in progress"
            if st.session_state.timer_running
            else "Break paused"
        )
    else:
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

    if (
        st.session_state.timer_complete_notice
        and st.session_state.timer_phase == "Break"
    ):
        st.success(
            "Focus session completed and saved. Your break started automatically."
        )

    if st.session_state.timer_break_complete_notice:
        st.success(
            "Break complete. The next focus session is ready."
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

def dashboard_page(tasks: list[dict], availability: dict[str, dict]) -> None:
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

    available_hours = sum(
        availability_window_hours(values)
        for values in availability.values()
    )

    today_minutes, today_sessions = get_today_focus_stats()
    daily_goal = int(get_setting("daily_focus_goal", "60"))

    st.subheader("Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active tasks", len(active_tasks))
    m2.metric("Hours remaining", f"{remaining_hours:.1f}")
    m3.metric("Urgent / overdue", len(urgent_tasks))
    m4.metric("Weekly study time", f"{available_hours:.1f} hr")

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
        st.metric("Focused minutes", today_minutes)
        st.metric("Completed sessions", today_sessions)

        if today_minutes >= daily_goal:
            st.success("Daily focus goal reached.")
        elif today_sessions == 0:
            st.info("Start a focus timer session when you are ready.")
        else:
            st.info(
                f"{daily_goal - today_minutes} minutes left to reach your goal."
            )

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

    st.subheader("Pomodoro Focus Timer")
    st.caption(
        "Choose a preset or enter your own focus time. "
        "After each completed focus session, a 5, 10, or 15-minute break starts automatically."
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

    task_col, mode_col = st.columns([1.4, 1])

    with task_col:
        selected_label = st.selectbox(
            "Focus task",
            list(task_options.keys()),
            disabled=st.session_state.timer_running,
        )
        selected_task_id = task_options[selected_label]

    with mode_col:
        duration_mode = st.radio(
            "Focus duration",
            ["Preset", "Custom"],
            horizontal=True,
            disabled=st.session_state.timer_running,
        )

    duration_col, break_col = st.columns(2)

    with duration_col:
        if duration_mode == "Preset":
            selected_duration = st.selectbox(
                "Session length",
                [15, 25, 45, 60],
                index=1,
                format_func=lambda value: f"{value} minutes",
                disabled=st.session_state.timer_running,
            )
        else:
            selected_duration = int(
                st.number_input(
                    "Custom focus time (minutes)",
                    min_value=1,
                    max_value=240,
                    value=int(st.session_state.timer_focus_minutes),
                    step=1,
                    disabled=st.session_state.timer_running,
                )
            )

    with break_col:
        selected_break = st.selectbox(
            "Break duration",
            [5, 10, 15],
            index=[5, 10, 15].index(
                int(st.session_state.timer_break_minutes)
                if int(st.session_state.timer_break_minutes) in [5, 10, 15]
                else 5
            ),
            format_func=lambda value: f"{value} minutes",
            disabled=st.session_state.timer_running,
        )

    config = (
        selected_task_id,
        selected_duration,
        selected_break,
    )

    if (
        not st.session_state.timer_running
        and st.session_state.timer_config != config
    ):
        st.session_state.timer_config = config
        st.session_state.timer_task_id = selected_task_id
        st.session_state.timer_focus_minutes = selected_duration
        st.session_state.timer_break_minutes = selected_break
        st.session_state.timer_phase = "Focus"
        st.session_state.timer_remaining_seconds = selected_duration * 60
        st.session_state.timer_logged = False
        st.session_state.timer_complete_notice = False
        st.session_state.timer_break_complete_notice = False

    current_phase = st.session_state.timer_phase

    if current_phase == "Break":
        start_label = "▶ Resume Break"
    elif (
        st.session_state.timer_remaining_seconds
        < st.session_state.timer_focus_minutes * 60
    ):
        start_label = "▶ Resume Focus"
    else:
        start_label = "▶ Start Focus"

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if st.button(
            start_label,
            type="primary",
            use_container_width=True,
            disabled=st.session_state.timer_running,
        ):
            if st.session_state.timer_remaining_seconds <= 0:
                if st.session_state.timer_phase == "Break":
                    st.session_state.timer_remaining_seconds = (
                        selected_break * 60
                    )
                else:
                    st.session_state.timer_remaining_seconds = (
                        selected_duration * 60
                    )

            st.session_state.timer_task_id = selected_task_id
            st.session_state.timer_focus_minutes = selected_duration
            st.session_state.timer_break_minutes = selected_break
            st.session_state.timer_end_timestamp = (
                time_module.time()
                + st.session_state.timer_remaining_seconds
            )
            st.session_state.timer_running = True
            st.session_state.timer_break_complete_notice = False

            if st.session_state.timer_phase == "Focus":
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
            st.session_state.timer_phase = "Focus"
            st.session_state.timer_remaining_seconds = selected_duration * 60
            st.session_state.timer_focus_minutes = selected_duration
            st.session_state.timer_break_minutes = selected_break
            st.session_state.timer_task_id = selected_task_id
            st.session_state.timer_logged = False
            st.session_state.timer_complete_notice = False
            st.session_state.timer_break_complete_notice = False
            st.rerun()

    with b4:
        if st.button(
            "⏭ Skip Break",
            use_container_width=True,
            disabled=st.session_state.timer_phase != "Break",
        ):
            st.session_state.timer_running = False
            st.session_state.timer_phase = "Focus"
            st.session_state.timer_remaining_seconds = selected_duration * 60
            st.session_state.timer_logged = False
            st.session_state.timer_complete_notice = False
            st.session_state.timer_break_complete_notice = True
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
                    <span style="color:var(--text-soft);">
                        {session["minutes"]} focus minutes · {completed_at}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )



def study_plan_page(
    tasks: list[dict],
    availability: dict[str, dict],
) -> None:
    st.subheader("Study Plan")
    st.caption(
        "Choose the exact times you are free each day. "
        "StudyFlow will place sessions inside those time windows."
    )

    with st.expander("Weekly study times", expanded=True):
        st.markdown(
            "**Select the days you can study, then choose a start and end time.**"
        )

        with st.form("availability_form"):
            updated_windows: dict[str, dict] = {}

            for day_name in DAYS:
                values = availability[day_name]
                enabled_value = bool(values["enabled"])

                day_col, start_col, end_col = st.columns([1.1, 1, 1])

                with day_col:
                    enabled = st.checkbox(
                        day_name,
                        value=enabled_value,
                        key=f"available_{day_name}",
                    )

                with start_col:
                    start_value = st.time_input(
                        f"{day_name} start",
                        value=time.fromisoformat(values["start"]),
                        key=f"start_{day_name}",
                        disabled=not enabled,
                        label_visibility="collapsed",
                    )

                with end_col:
                    end_value = st.time_input(
                        f"{day_name} end",
                        value=time.fromisoformat(values["end"]),
                        key=f"end_{day_name}",
                        disabled=not enabled,
                        label_visibility="collapsed",
                    )

                updated_windows[day_name] = {
                    "enabled": enabled,
                    "start": start_value.strftime("%H:%M"),
                    "end": end_value.strftime("%H:%M"),
                }

            save_times = st.form_submit_button(
                "Save weekly study times",
                type="primary",
                use_container_width=True,
            )

        if save_times:
            invalid_days = [
                day_name
                for day_name, values in updated_windows.items()
                if values["enabled"]
                and time.fromisoformat(values["end"])
                <= time.fromisoformat(values["start"])
            ]

            if invalid_days:
                st.error(
                    "The end time must be later than the start time for: "
                    + ", ".join(invalid_days)
                )
            else:
                save_availability(updated_windows)
                st.success("Weekly study times saved.")
                st.rerun()

    current_windows = []

    for day_name in DAYS:
        values = availability[day_name]

        if values["enabled"]:
            start_text = time.fromisoformat(values["start"]).strftime(
                "%I:%M %p"
            ).lstrip("0")
            end_text = time.fromisoformat(values["end"]).strftime(
                "%I:%M %p"
            ).lstrip("0")
            window_text = f"{start_text}–{end_text}"
            hours_text = f"{availability_window_hours(values):.1f} hr"
        else:
            window_text = "Unavailable"
            hours_text = "0 hr"

        current_windows.append(
            {
                "Day": day_name,
                "Available Time": window_text,
                "Length": hours_text,
            }
        )

    st.dataframe(
        pd.DataFrame(current_windows),
        use_container_width=True,
        hide_index=True,
    )

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
            "No sessions could be scheduled. "
            "Choose at least one future study-time window."
        )
        return

    total_minutes = 0

    for row in schedule:
        study_text = row["Study Time"]

        if study_text.endswith(" hr"):
            total_minutes += int(
                round(float(study_text.replace(" hr", "")) * 60)
            )
        else:
            total_minutes += int(study_text.replace(" min", ""))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Study sessions", len(schedule))
    c2.metric("Scheduled hours", f"{total_minutes / 60:.1f}")
    c3.metric(
        "Tasks included",
        len({row["Task"] for row in schedule}),
    )
    c4.metric(
        "Available this week",
        f"{sum(availability_window_hours(v) for v in availability.values()):.1f} hr",
    )

    display_rows = []

    for row in schedule:
        display_rows.append(
            {
                "Date": row["Date"].strftime("%b %d, %Y"),
                "Day": row["Day"],
                "Time": row["Time"],
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
                        <strong>{session["Time"]} · {safe_subject}: {safe_task}</strong><br>
                        <span style="color:var(--text-soft);">
                            {session["Study Time"]} ·
                            {session["Priority"]} priority ·
                            {session["Status"]}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if warnings:
        st.warning("Some work did not fit into the available times.")
        for warning in warnings:
            st.write(f"• {warning}")



def additional_resources_page() -> None:
    st.subheader("Additional Resources")
    st.caption(
        "Search and watch educational videos, save useful links, "
        "and open trusted study tools."
    )

    youtube_tab, saved_tab, tools_tab = st.tabs(
        [
            "▶ YouTube Watcher",
            "🔖 My Resources",
            "🧰 Study Tools",
        ]
    )

    with youtube_tab:
        youtube_api_key = get_default_youtube_api_key()

        st.markdown(
            """
            <div class="youtube-shell">
                <div class="youtube-brand-row">
                    <div class="youtube-play-mark">▶</div>
                    <div>
                        <div class="youtube-watcher-title">YouTube Watcher</div>
                        <div class="youtube-watcher-subtitle">
                            Search a topic or channel and watch videos without leaving StudyFlow.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if youtube_api_key:
            st.success("YouTube Watcher is connected.")
        else:
            st.error(
                "YouTube Watcher is not connected. Add YOUTUBE_API_KEY "
                "to your Streamlit or Codespaces secrets and restart the app."
            )

        with st.container(border=True):
            with st.form(
                "youtube_watcher_search_form",
                clear_on_submit=False,
                border=False,
            ):
                search_query = st.text_input(
                    "Search YouTube",
                    value=st.session_state.get(
                        "youtube_watcher_query",
                        "",
                    ),
                    placeholder="Search a topic, lesson, creator, or @channel...",
                    label_visibility="collapsed",
                )

                st.markdown(
                    '<div class="youtube-search-help">'
                    'Examples: “calculus limits,” “Python recursion,” '
                    '“Khan Academy,” or “@3blue1brown”'
                    "</div>",
                    unsafe_allow_html=True,
                )

                (
                    mode_col,
                    type_col,
                    order_col,
                    button_col,
                ) = st.columns([1.15, 1.15, 1.15, 0.85])

                with mode_col:
                    search_mode = st.radio(
                        "Search for",
                        ["Topic", "Channel"],
                        horizontal=True,
                        index=(
                            1
                            if st.session_state.get(
                                "youtube_watcher_mode"
                            ) == "Channel"
                            else 0
                        ),
                    )

                with type_col:
                    video_type_options = [
                        "Everything",
                        "Videos",
                        "Shorts",
                    ]
                    saved_video_type = st.session_state.get(
                        "youtube_watcher_video_type",
                        "Everything",
                    )
                    video_type = st.selectbox(
                        "Type",
                        video_type_options,
                        index=video_type_options.index(
                            saved_video_type
                            if saved_video_type in video_type_options
                            else "Everything"
                        ),
                    )

                with order_col:
                    order_options = [
                        "Relevant",
                        "Newest",
                        "Most viewed",
                    ]
                    saved_order = st.session_state.get(
                        "youtube_watcher_order",
                        "Relevant",
                    )
                    sort_order = st.selectbox(
                        "Sort",
                        order_options,
                        index=order_options.index(
                            saved_order
                            if saved_order in order_options
                            else "Relevant"
                        ),
                    )

                with button_col:
                    st.write("")
                    search_submitted = st.form_submit_button(
                        "🔍 Search",
                        type="primary",
                        use_container_width=True,
                    )

        if search_submitted:
            if not youtube_api_key:
                st.error(
                    "YouTube Watcher is not connected yet."
                )
            elif not search_query.strip():
                st.warning(
                    "Enter a topic or channel before searching."
                )
            else:
                try:
                    with st.spinner("Searching YouTube..."):
                        (
                            videos,
                            next_page_token,
                            total_results,
                            resolved_label,
                        ) = search_youtube_watcher(
                            search_query,
                            youtube_api_key,
                            search_mode,
                            sort_order,
                            video_type,
                            max_results=12,
                        )

                    st.session_state.youtube_watcher_query = (
                        search_query.strip()
                    )
                    st.session_state.youtube_watcher_mode = (
                        search_mode
                    )
                    st.session_state.youtube_watcher_order = (
                        sort_order
                    )
                    st.session_state.youtube_watcher_video_type = (
                        video_type
                    )
                    st.session_state.youtube_watcher_results = videos
                    st.session_state.youtube_watcher_next_token = (
                        next_page_token
                    )
                    st.session_state.youtube_watcher_total = (
                        total_results
                    )
                    st.session_state.youtube_watcher_label = (
                        resolved_label
                    )
                    st.session_state.youtube_watcher_selected = (
                        videos[0]
                        if videos and video_type != "Shorts"
                        else None
                    )
                    st.session_state.youtube_watcher_error = ""
                except RuntimeError as error:
                    st.session_state.youtube_watcher_results = []
                    st.session_state.youtube_watcher_next_token = ""
                    st.session_state.youtube_watcher_error = str(error)

        watcher_error = st.session_state.get(
            "youtube_watcher_error",
            "",
        )

        if watcher_error:
            st.error(watcher_error)

        videos = st.session_state.get(
            "youtube_watcher_results",
            [],
        )
        selected_video = st.session_state.get(
            "youtube_watcher_selected"
        )

selected_video_type = st.session_state.get(
    "youtube_watcher_video_type",
    "Everything",
)

if selected_video and selected_video_type != "Shorts":
    safe_player_title = html.escape(
        selected_video["title"]
    )
    safe_player_channel = html.escape(
        selected_video["channel"]
    )
    duration_text = selected_video.get(
        "duration_text",
        "Duration unavailable",
    )

    st.markdown(
        f"""
        <div class="youtube-player-box">
            <div class="youtube-player-title">
                {safe_player_title}
            </div>
            <div class="youtube-player-meta">
                {safe_player_channel} ·
                {format_youtube_date(selected_video["published_at"])}
                · {duration_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.video(selected_video["url"])

if videos:
    result_label = html.escape(
        str(
            st.session_state.get(
                "youtube_watcher_label",
                st.session_state.get(
                    "youtube_watcher_query",
                    "",
                ),
            )
        )
    )
    total_results = st.session_state.get(
        "youtube_watcher_total",
        0,
    )

    heading_name = (
        "Shorts"
        if selected_video_type == "Shorts"
        else "Videos"
    )

    st.markdown(
        f"### {heading_name} for “{result_label}”"
    )
    st.caption(
        f"Showing {len(videos)} result(s)"
        + (
            f" from approximately {total_results:,} matches."
            if total_results
            else "."
        )
    )

    if selected_video_type == "Shorts":
        st.markdown(
            """
            <div class="shorts-note">
                Scroll inside the Shorts box, use your mouse wheel or
                trackpad, or click the ↑ and ↓ buttons to move between Shorts.
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_shorts_scroll_feed(
            videos,
            st.session_state.app_theme,
        )
    else:
        for row_start in range(0, len(videos), 3):
            columns = st.columns(3)
            row_videos = videos[
                row_start:row_start + 3
            ]

            for offset, (column, video) in enumerate(
                zip(columns, row_videos)
            ):
                result_index = row_start + offset

                with column:
                    with st.container(border=True):
                        if video["thumbnail"]:
                            st.image(
                                video["thumbnail"],
                                use_container_width=True,
                            )

                        safe_title = html.escape(
                            shorten_text(
                                video["title"],
                                92,
                            )
                        )
                        safe_channel = html.escape(
                            video["channel"]
                        )
                        date_text = format_youtube_date(
                            video["published_at"]
                        )
                        duration_text = video.get(
                            "duration_text",
                            "Duration unavailable",
                        )
                        type_text = video.get(
                            "video_type",
                            "Video",
                        )

                        st.markdown(
                            f"""
                            <div class="youtube-result-title">
                                {safe_title}
                            </div>
                            <div class="youtube-result-meta">
                                {safe_channel}<br>
                                {date_text} · {duration_text}
                            </div>
                            <span class="video-type-badge">
                                {type_text}
                            </span>
                            """,
                            unsafe_allow_html=True,
                        )

                        watch_col, open_col = st.columns(2)

                        with watch_col:
                            if st.button(
                                "▶ Watch",
                                key=(
                                    "watch_youtube_"
                                    f"{video['video_id']}_"
                                    f"{result_index}"
                                ),
                                use_container_width=True,
                            ):
                                st.session_state[
                                    "youtube_watcher_selected"
                                ] = video
                                st.rerun()

                        with open_col:
                            st.link_button(
                                "Open ↗",
                                video["url"],
                                use_container_width=True,
                            )

    next_page_token = st.session_state.get(
        "youtube_watcher_next_token",
        "",
    )

    if next_page_token:
        spacer_left, more_col, spacer_right = st.columns(
            [1.5, 1, 1.5]
        )

        with more_col:
            button_label = (
                "Show more Shorts"
                if selected_video_type == "Shorts"
                else "Show more videos"
            )

            if st.button(
                button_label,
                type="primary",
                use_container_width=True,
            ):
                try:
                    with st.spinner(
                        "Loading more results..."
                    ):
                        (
                            more_videos,
                            new_next_token,
                            total_results,
                            resolved_label,
                        ) = search_youtube_watcher(
                            st.session_state[
                                "youtube_watcher_query"
                            ],
                            youtube_api_key,
                            st.session_state[
                                "youtube_watcher_mode"
                            ],
                            st.session_state[
                                "youtube_watcher_order"
                            ],
                            st.session_state.get(
                                "youtube_watcher_video_type",
                                "Everything",
                            ),
                            page_token=next_page_token,
                            max_results=12,
                        )

                    existing_ids = {
                        video["video_id"]
                        for video in videos
                    }
                    unique_more = [
                        video
                        for video in more_videos
                        if video["video_id"]
                        not in existing_ids
                    ]

                    st.session_state[
                        "youtube_watcher_results"
                    ] = videos + unique_more
                    st.session_state[
                        "youtube_watcher_next_token"
                    ] = new_next_token
                    st.session_state[
                        "youtube_watcher_total"
                    ] = total_results
                    st.rerun()
                except RuntimeError as error:
                    st.error(str(error))
else:
    st.markdown(
        """
        <div class="youtube-empty">
            <strong>Search for something to watch.</strong><br>
            Find lessons, tutorials, creators, videos, or Shorts.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with saved_tab:
        st.markdown(
            '<div class="section-eyebrow">Personal library</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Save useful study resources")

        with st.form(
            "add_study_resource_form",
            clear_on_submit=True,
        ):
            resource_left, resource_right = st.columns(2)

            with resource_left:
                resource_title = st.text_input(
                    "Resource title",
                    placeholder="Example: Algebra practice problems",
                )
                resource_url = st.text_input(
                    "Resource URL",
                    placeholder="https://...",
                )

            with resource_right:
                resource_category = st.selectbox(
                    "Category",
                    [
                        "Website",
                        "Video",
                        "Article",
                        "Practice",
                        "Reference",
                        "Other",
                    ],
                )
                resource_notes = st.text_area(
                    "Notes",
                    placeholder="Why this resource is useful...",
                    height=96,
                )

            save_resource_button = st.form_submit_button(
                "Save resource",
                type="primary",
                use_container_width=True,
            )

        if save_resource_button:
            if (
                not resource_title.strip()
                or not resource_url.strip()
            ):
                st.error("Enter both a title and URL.")
            else:
                success, message = add_study_resource(
                    resource_title,
                    resource_url,
                    resource_category,
                    resource_notes,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        resources = get_study_resources()

        if not resources:
            st.info("Your saved resource library is empty.")
        else:
            category_options = ["All categories"] + sorted(
                {
                    resource["category"]
                    for resource in resources
                }
            )

            resource_category_filter = st.selectbox(
                "Filter resources",
                category_options,
            )

            filtered_resources = resources

            if resource_category_filter != "All categories":
                filtered_resources = [
                    resource
                    for resource in resources
                    if resource["category"]
                    == resource_category_filter
                ]

            for resource in filtered_resources:
                safe_title = html.escape(resource["title"])
                safe_category = html.escape(
                    resource["category"]
                )
                safe_notes = html.escape(
                    resource["notes"]
                    or "No notes were added."
                )

                st.markdown(
                    f"""
                    <div class="resource-card">
                        <h4>{safe_title}</h4>
                        <span class="badge teal">{safe_category}</span>
                        <div class="resource-description"
                             style="margin-top:0.55rem;">
                            {safe_notes}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                open_col, delete_col = st.columns([3, 1])

                with open_col:
                    st.link_button(
                        "Open resource",
                        resource["resource_url"],
                        use_container_width=True,
                    )

                with delete_col:
                    if st.button(
                        "Delete",
                        key=f"delete_resource_{resource['id']}",
                        use_container_width=True,
                    ):
                        delete_study_resource(resource["id"])
                        st.success("Resource deleted.")
                        st.rerun()

    with tools_tab:
        st.markdown(
            '<div class="section-eyebrow">Quick access</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Useful study tools")

        study_tools = [
            {
                "name": "Khan Academy",
                "description": (
                    "Lessons and practice across mathematics, "
                    "science, computing, economics, and more."
                ),
                "url": "https://www.khanacademy.org/",
            },
            {
                "name": "Desmos",
                "description": (
                    "Graphing calculator and interactive "
                    "mathematics tools."
                ),
                "url": "https://www.desmos.com/calculator",
            },
            {
                "name": "WolframAlpha",
                "description": (
                    "Computational answers, formulas, graphs, "
                    "and step-based mathematical exploration."
                ),
                "url": "https://www.wolframalpha.com/",
            },
            {
                "name": "Quizlet",
                "description": (
                    "Flashcards and study sets for vocabulary, "
                    "definitions, and review."
                ),
                "url": "https://quizlet.com/",
            },
            {
                "name": "Google Scholar",
                "description": (
                    "Search scholarly articles, books, papers, "
                    "and academic sources."
                ),
                "url": "https://scholar.google.com/",
            },
            {
                "name": "Project Gutenberg",
                "description": (
                    "A large collection of free public-domain "
                    "ebooks and classic literature."
                ),
                "url": "https://www.gutenberg.org/",
            },
        ]

        for index in range(0, len(study_tools), 2):
            columns = st.columns(2)

            for column, tool in zip(
                columns,
                study_tools[index:index + 2],
            ):
                with column:
                    st.markdown(
                        f"""
                        <div class="tool-card">
                            <h4>{html.escape(tool["name"])}</h4>
                            <div class="tool-description">
                                {html.escape(tool["description"])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.link_button(
                        f"Open {tool['name']}",
                        tool["url"],
                        use_container_width=True,
                    )



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

    st.markdown(
        '<div class="theme-label">Appearance</div>',
        unsafe_allow_html=True,
    )

    dark_mode_enabled = st.toggle(
        "🌙 Dark mode",
        value=st.session_state.app_theme == "Dark",
        help="Turn this off to use the high-contrast light theme.",
    )

    requested_theme = "Dark" if dark_mode_enabled else "Light"

    if requested_theme != st.session_state.app_theme:
        st.session_state.app_theme = requested_theme
        st.rerun()

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Task",
            "✅ My Tasks",
            "⏱️ Focus Timer",
            "🗓️ Study Plan",
            "📚 Additional Resources",
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
elif page == "🗓️ Study Plan":
    study_plan_page(tasks, availability)
else:
    additional_resources_page()