from __future__ import annotations
import pandas as pd
from health_report.common.config import REPORT_END_DATE


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    x = df.set_index("Date").resample("MS").agg({
        "Weight kg": "mean",
        "Fat mass kg": "mean",
        "Lean mass kg": "mean",
    }).dropna(how="all")
    x.index = x.index.strftime("%Y-%m")
    x = x.rename(columns={"Weight kg": "Weight", "Fat mass kg": "Fat Mass", "Lean mass kg": "Lean Mass"})
    return x.round(2)


def first_last_metrics(df: pd.DataFrame) -> pd.DataFrame:
    cols = [("Weight kg", "Weight"), ("Fat mass kg", "Fat Mass"), ("Lean mass kg", "Lean Mass")]
    rows = []
    body = df.dropna(subset=["Weight kg", "Fat mass kg", "Lean mass kg"], how="all")
    months = ((body["Date"].max() - body["Date"].min()).days) / 30.4375
    weeks = ((body["Date"].max() - body["Date"].min()).days) / 7
    for col, name in cols:
        s = body[["Date", col]].dropna()
        start = float(s.iloc[0][col])
        end = float(s.iloc[-1][col])
        delta = end - start
        rows.append({
            "Metric": name,
            "Start": start,
            "End": end,
            "Delta kg": delta,
            "Delta %": delta / start * 100,
            "kg/month": delta / months,
            "g/week": delta / weeks * 1000,
        })
    return pd.DataFrame(rows).round({"Start": 2, "End": 2, "Delta kg": 2, "Delta %": 1, "kg/month": 3, "g/week": 1})


def phase_summary(df: pd.DataFrame) -> pd.DataFrame:
    phases = [
        ("Baseline / pre-drift", "2025-08-01", "2025-09-30"),
        ("Phase I: early drift / lean-dominant adaptation", "2025-10-01", "2026-01-31"),
        ("Phase II: mixed transition", "2026-02-01", "2026-04-30"),
        ("Phase III: fat-dominant period", "2026-05-01", REPORT_END_DATE),
    ]
    rows = []
    for name, start, end in phases:
        sub = df[(df["Date"] >= pd.Timestamp(start)) & (df["Date"] <= pd.Timestamp(end))]
        row = {"Phase": name, "Start": "", "End": "", "Days": len(sub)}
        for col, label in [("Weight kg", "Weight"), ("Fat mass kg", "Fat"), ("Lean mass kg", "Lean")]:
            s = sub[["Date", col]].dropna()
            if len(s) >= 2:
                if row["Start"] == "":
                    row["Start"] = str(s.iloc[0]["Date"].date())
                row["End"] = str(s.iloc[-1]["Date"].date())
                row[f"{label} start"] = float(s.iloc[0][col])
                row[f"{label} end"] = float(s.iloc[-1][col])
                row[f"{label} Δ kg"] = float(s.iloc[-1][col] - s.iloc[0][col])
        rows.append(row)
    return pd.DataFrame(rows).round(2)
