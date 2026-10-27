"""
Task due-date reminder
----------------------
Reads an Excel file and shows a popup for tasks that are due within the
next N days (default: 7), plus any overdue tasks.

Install once:
    pip install pandas openpyxl

Run:
    python due_date_reminder.py
"""

import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta

import pandas as pd

# ---------------- SETTINGS (edit these) ----------------
EXCEL_FILE = r"E:\Sample\tasks.xlsx"      # full path to your Excel file
SHEET_NAME = 0                  # sheet name (e.g. "Sheet1") or index (0 = first sheet)
TASK_COLUMN = "Task"            # header of the column with task names
DUE_COLUMN = "Due Date"         # header of the column with due dates
STATUS_COLUMN = "Status"        # optional; set to None if you don't have one
DONE_VALUES = {"done", "completed", "closed"}  # statuses to ignore
REMIND_DAYS = 7                 # how many days before due date to remind
SHOW_OVERDUE = True             # also remind about overdue tasks
# --------------------------------------------------------


def load_tasks():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    df.columns = [str(c).strip() for c in df.columns]

    for col in (TASK_COLUMN, DUE_COLUMN):
        if col not in df.columns:
            raise KeyError(
                f"Column '{col}' not found. Columns in file: {list(df.columns)}"
            )

    df[DUE_COLUMN] = pd.to_datetime(df[DUE_COLUMN], errors="coerce").dt.date
    df = df.dropna(subset=[DUE_COLUMN])

    # Skip tasks already completed
    if STATUS_COLUMN and STATUS_COLUMN in df.columns:
        status = df[STATUS_COLUMN].astype(str).str.strip().str.lower()
        df = df[~status.isin(DONE_VALUES)]

    return df


def build_message(df):
    today = date.today()
    limit = today + timedelta(days=REMIND_DAYS)

    upcoming, overdue = [], []
    for _, row in df.iterrows():
        due = row[DUE_COLUMN]
        name = row[TASK_COLUMN]
        days_left = (due - today).days
        if due < today:
            overdue.append((due, name, days_left))
        elif due <= limit:
            upcoming.append((due, name, days_left))

    upcoming.sort()
    overdue.sort()

    lines = []
    if upcoming:
        lines.append(f"Due within the next {REMIND_DAYS} days:\n")
        for due, name, d in upcoming:
            when = "TODAY" if d == 0 else f"in {d} day(s)"
            lines.append(f"  • {name} — {due:%d %b %Y} ({when})")
    if SHOW_OVERDUE and overdue:
        if lines:
            lines.append("")
        lines.append("OVERDUE:\n")
        for due, name, d in overdue:
            lines.append(f"  • {name} — was due {due:%d %b %Y} ({abs(d)} day(s) ago)")

    return "\n".join(lines)


def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()                      # hide the empty main window
    root.attributes("-topmost", True)    # keep popup above other windows
    messagebox.showinfo(title, message)
    root.destroy()


def main():
    try:
        df = load_tasks()
    except Exception as e:
        show_popup("Reminder error", f"Could not read the Excel file:\n\n{e}")
        return

    message = build_message(df)
    if message:
        show_popup("Task Reminder", message)
    # If nothing is due, stay silent.


if __name__ == "__main__":
    main()