from __future__ import annotations
import pandas as pd


def load_withings(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Load Withings body-composition data from Weight Data sheet."""
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
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]
    # Multiple records per day are averaged.
    df = df.groupby("Date", as_index=False).mean(numeric_only=True)
    return df
