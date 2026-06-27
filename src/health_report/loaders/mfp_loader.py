from __future__ import annotations
import pandas as pd


def load_mfp_daily(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Load daily MyFitnessPal totals from parsed workbook."""
    df = pd.read_excel(path, sheet_name="Daily Totals")
    df["Date"] = pd.to_datetime(df["date"]).dt.normalize()
    rename = {
        "calories": "Calories In",
        "protein": "Protein g",
        "fat": "Fat g",
        "carbs": "Carbs g",
        "fiber": "Fiber g",
        "sugar": "Sugar g",
    }
    df = df.rename(columns=rename)
    keep = ["Date", "Calories In", "Protein g", "Fat g", "Carbs g", "Fiber g", "Sugar g", "protein_per_1000", "fiber_per_1000"]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].copy()
    for c in keep:
        if c != "Date":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    return df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
