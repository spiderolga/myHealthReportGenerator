from __future__ import annotations
import pandas as pd


def load_events(path: str, start_date: str, end_date: str) -> pd.DataFrame:
    ev = pd.read_csv(path)
    ev["start"] = pd.to_datetime(ev["start"]).dt.normalize()
    ev["end"] = pd.to_datetime(ev["end"]).dt.normalize()
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    ev = ev[(ev["end"] >= start) & (ev["start"] <= end)].copy()
    return ev


def add_event_flags(master: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    out = master.copy()
    flags = {
        "Travel": "Travel",
        "HRT": "HRT",
        "RA": "RA flare",
        "Training": "Training intervention",
        "Medication": "Medication",
        "Nutrition": "Nutrition intervention",
    }
    for col in flags:
        out[col] = False
    out["Event labels"] = ""
    for _, row in events.iterrows():
        mask = (out["Date"] >= row["start"]) & (out["Date"] <= row["end"])
        category = str(row["category"])
        if category in out.columns:
            out.loc[mask, category] = True
        label = str(row.get("label", ""))
        out.loc[mask, "Event labels"] = out.loc[mask, "Event labels"].apply(lambda x: (x + "; " if x else "") + label)
    return out
