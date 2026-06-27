from __future__ import annotations
import calendar
import pandas as pd

NUTRITION_COLUMNS = ["Calories In", "Protein g", "Fat g", "Carbs g", "Fiber g", "Sugar g"]


def add_nutrition_derived(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Calories In" in out.columns:
        calories = pd.to_numeric(out["Calories In"], errors="coerce")
        protein = pd.to_numeric(out.get("Protein g"), errors="coerce")
        fiber = pd.to_numeric(out.get("Fiber g"), errors="coerce")
        lean = pd.to_numeric(out.get("Lean mass kg"), errors="coerce")
        out["Food Logged"] = calories.notna() & (calories > 0)
        out["Protein per 1000 kcal"] = protein / calories * 1000
        out["Fiber per 1000 kcal"] = fiber / calories * 1000
        out["Protein Efficiency Index"] = protein / calories * 100
        out["Protein per Lean kg"] = protein / lean
    return out


def food_diary_coverage(df: pd.DataFrame) -> pd.DataFrame:
    data = add_nutrition_derived(df)
    data["MonthStart"] = data["Date"].dt.to_period("M").dt.to_timestamp()
    rows = []
    for month, sub in data.groupby("MonthStart", sort=True):
        logged = int(sub["Food Logged"].sum())
        days = len(sub)
        rows.append({
            "Month": month.strftime("%Y-%m"),
            "Days": days,
            "Logged days": logged,
            "Coverage %": round(logged / days * 100, 1) if days else 0.0,
        })
    return pd.DataFrame(rows)


def detect_nutrition_phases(df: pd.DataFrame, min_logged_days: int = 5, min_coverage: float = 15.0) -> pd.DataFrame:
    coverage = food_diary_coverage(df)
    coverage["Eligible"] = (coverage["Logged days"] >= min_logged_days) & (coverage["Coverage %"] >= min_coverage)
    phases = []
    current = []
    for _, row in coverage.iterrows():
        if bool(row["Eligible"]):
            current.append(row)
        else:
            if current:
                phases.append(current)
                current = []
    if current:
        phases.append(current)

    rows = []
    for i, group in enumerate(phases, start=1):
        start_month = pd.Timestamp(group[0]["Month"] + "-01")
        end_month_start = pd.Timestamp(group[-1]["Month"] + "-01")
        end_day = calendar.monthrange(end_month_start.year, end_month_start.month)[1]
        end_month = end_month_start.replace(day=end_day)
        df_end = pd.Timestamp(df["Date"].max())
        end_month = min(end_month, df_end)
        sub = df[(df["Date"] >= start_month) & (df["Date"] <= end_month)].copy()
        logged = add_nutrition_derived(sub)
        logged_days = int(logged["Food Logged"].sum())
        days = len(logged)
        rows.append({
            "Phase": f"Nutrition Phase {i}",
            "Start": str(start_month.date()),
            "End": str(end_month.date()),
            "Days": days,
            "Logged days": logged_days,
            "Coverage %": round(logged_days / days * 100, 1) if days else 0.0,
        })
    return pd.DataFrame(rows)


def nutrition_phase_summary(df: pd.DataFrame, phases: pd.DataFrame) -> pd.DataFrame:
    data = add_nutrition_derived(df)
    rows = []
    for _, p in phases.iterrows():
        start = pd.Timestamp(p["Start"])
        end = pd.Timestamp(p["End"])
        sub = data[(data["Date"] >= start) & (data["Date"] <= end) & (data["Food Logged"])].copy()
        row = {
            "Phase": p["Phase"],
            "Period": f"{p['Start']} to {p['End']}",
            "Logged days": int(len(sub)),
            "Coverage %": p["Coverage %"],
        }
        for col, label in [
            ("Calories In", "kcal/day"),
            ("Protein g", "Protein g"),
            ("Fat g", "Fat g"),
            ("Carbs g", "Carbs g"),
            ("Fiber g", "Fiber g"),
            ("Protein per 1000 kcal", "Protein g/1000 kcal"),
            ("Protein Efficiency Index", "PEI g/100 kcal"),
        ]:
            if col in sub.columns and len(sub):
                row[label] = round(float(sub[col].mean()), 1)
        rows.append(row)
    return pd.DataFrame(rows)
