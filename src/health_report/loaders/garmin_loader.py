from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_garmin_daily(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Garmin Daily Calories")
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    df = df.rename(columns={
        "Active Calories": "Garmin Active Calories",
        "Resting Calories": "Garmin Resting Calories",
        "Total Calories": "Garmin Total Calories",
    })
    for c in ["Garmin Active Calories", "Garmin Resting Calories", "Garmin Total Calories"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    return df[(df["Date"] >= start) & (df["Date"] <= end)].copy()


def _to_minutes(x) -> float:
    if pd.isna(x):
        return 0.0
    s = str(x).strip()
    try:
        parts = s.split(":")
        if len(parts) == 3:
            h, m, sec = map(float, parts)
            return h * 60 + m + sec / 60
        if len(parts) == 2:
            m, sec = map(float, parts)
            return m + sec / 60
    except Exception:
        return 0.0
    return 0.0


def _num(x) -> float:
    if pd.isna(x):
        return 0.0
    s = str(x).strip().replace(",", "")
    if s in {"", "--"}:
        return 0.0
    # Garmin sometimes exports body battery values like '-4 with a leading apostrophe.
    s = s.replace("'", "")
    v = pd.to_numeric(s, errors="coerce")
    return 0.0 if pd.isna(v) else float(v)


def _finalize_activities(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "Date",
            "Activity Count",
            "Activity Duration min",
            "Activity Calories",
            "Activity Steps",
            "Badminton Count",
            "Badminton Duration min",
            "Badminton Calories",
            "Strength Count",
            "Strength Duration min",
            "Strength Calories",
            "Walking Count",
            "Walking Duration min",
            "Walking Calories",
        ])

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    df = df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
    if df.empty:
        return _finalize_activities(pd.DataFrame(), start_date, end_date)

    df["Activity Duration min"] = df["Time"].apply(_to_minutes) if "Time" in df.columns else 0.0
    df["Activity Calories"] = df["Calories"].apply(_num) if "Calories" in df.columns else 0.0
    df["Activity Steps"] = df["Steps"].apply(_num) if "Steps" in df.columns else 0.0

    activity_type = df.get("Activity Type", pd.Series(index=df.index, dtype="object")).astype(str).str.lower()
    title = df.get("Title", pd.Series(index=df.index, dtype="object")).astype(str).str.lower()
    combined = activity_type + " " + title

    df["Badminton Count"] = combined.str.contains("badminton", na=False).astype(int)
    df["Strength Count"] = combined.str.contains("strength|weight training|gym", na=False, regex=True).astype(int)
    df["Walking Count"] = combined.str.contains("walking|walk", na=False, regex=True).astype(int)

    df["Badminton Duration min"] = df["Activity Duration min"] * df["Badminton Count"]
    df["Badminton Calories"] = df["Activity Calories"] * df["Badminton Count"]
    df["Strength Duration min"] = df["Activity Duration min"] * df["Strength Count"]
    df["Strength Calories"] = df["Activity Calories"] * df["Strength Count"]
    df["Walking Duration min"] = df["Activity Duration min"] * df["Walking Count"]
    df["Walking Calories"] = df["Activity Calories"] * df["Walking Count"]

    out = df.groupby("Date", as_index=False).agg({
        "Activity Type": "count",
        "Activity Duration min": "sum",
        "Activity Calories": "sum",
        "Activity Steps": "sum",
        "Badminton Count": "sum",
        "Badminton Duration min": "sum",
        "Badminton Calories": "sum",
        "Strength Count": "sum",
        "Strength Duration min": "sum",
        "Strength Calories": "sum",
        "Walking Count": "sum",
        "Walking Duration min": "sum",
        "Walking Calories": "sum",
    }).rename(columns={"Activity Type": "Activity Count"})
    return out


def load_activities_from_excel(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Activities")
    return _finalize_activities(df, start_date, end_date)


def load_activities_from_csv(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    return _finalize_activities(df, start_date, end_date)


def load_activities(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Load Garmin activities.

    Preferred input: Garmin CSV export, e.g. data/garmin/Activities.csv.
    Backward-compatible fallback: Activities sheet inside the legacy workbook.
    """
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return load_activities_from_csv(str(p), start_date, end_date)
    return load_activities_from_excel(str(p), start_date, end_date)
