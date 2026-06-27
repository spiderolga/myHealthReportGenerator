from __future__ import annotations
from pathlib import Path
import pandas as pd


def _load_withings_csv(path: str) -> pd.DataFrame:
    """Load Withings CSV export.

    The current Withings CSV export has a quoted first header row that pandas may
    interpret as a single column. We therefore skip the header row and assign the
    canonical column names explicitly.
    """
    columns = [
        "Date",
        "Weight kg",
        "Fat mass kg",
        "Bone mass kg",
        "Muscle mass kg",
        "Hydration kg",
        "Comments",
    ]
    df = pd.read_csv(path, skiprows=1, header=None, names=columns)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    for col in ["Weight kg", "Fat mass kg", "Bone mass kg", "Muscle mass kg", "Hydration kg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Lean mass kg"] = df["Weight kg"] - df["Fat mass kg"]
    return df[["Date", "Weight kg", "Fat mass kg", "Lean mass kg"]].copy()


def _load_withings_excel(path: str) -> pd.DataFrame:
    """Load Withings-like body-composition data from Weight Data sheet."""
    df = pd.read_excel(path, sheet_name="Weight Data")
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    rename = {
        "Weight_kg": "Weight kg",
        "FatMass_kg": "Fat mass kg",
        "LeanMass_kg": "Lean mass kg",
    }
    df = df.rename(columns=rename)
    keep = [c for c in ["Date", "Weight kg", "Fat mass kg", "Lean mass kg", "BMI"] if c in df.columns]
    df = df[keep].copy()
    for c in keep:
        if c != "Date":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_withings(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        df = _load_withings_csv(path)
    else:
        df = _load_withings_excel(path)

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]
    # Multiple records per day are averaged.
    df = df.groupby("Date", as_index=False).mean(numeric_only=True)
    return df
