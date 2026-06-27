# Personal Weight Regulation Report Generator

Reproducible Python report generator for the project:

**Body Composition Regulation After Successful Weight Loss - N-of-1 Case Study**

Current scope: Draft v0.7 - Version 2 architecture + Chapter 4 Body Composition Analysis.

## Version 2 architecture

The project now uses a daily master dataset as the central data layer. Raw Excel files are loaded once, merged by date, then all analysis and plots read from the same master dataframe.

```text
data/
  Health_Analytics_Database_DailySummary.xlsx
  MyFitnessPal_parsed_data.xlsx
  events.csv
  garmin/
    Activities.csv
  processed/
    master_dataframe.csv

src/
  generate_report.py
  health_report/
    loaders/
    preprocessing/
    analysis/
    visualization/
    report/
    common/

figures/
output/
report/
```

## Inputs

Place these files in `data/`:

- `Health_Analytics_Database_DailySummary.xlsx`
- `MyFitnessPal_parsed_data.xlsx`
- `events.csv`
- `garmin/Activities.csv` (optional but preferred for Garmin activity sessions)

## Run

Create and select a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Generate the report:

```powershell
generate-health-report

# or directly:
python src/generate_report.py
```

## Outputs

- `data/processed/master_dataframe.csv`
- `output/Personal_Weight_Regulation_Model_v0.7.pdf`
- `output/body_composition_metrics.csv`
- `output/monthly_body_composition.csv`
- `output/phase_summary.csv`
- figures in `figures/`

If an optional Parquet engine such as `pyarrow` is installed, `data/processed/master_dataframe.parquet` is also written. CSV remains canonical.

## Notes

- Withings Fat Mass and Lean Mass are treated as trend-level metrics, not clinical-grade body composition measurement.
- DEXA is not reproduced in Sprint 1.
- Garmin daily calories and Garmin activity sessions are loaded into the master dataframe. Activity sessions are categorized by title/type into Badminton, Strength, and Walking metrics.
- Nutrition variables are loaded into the master dataframe for Chapter 5.

## IntelliJ IDEA

Open this folder as a Python project.

Recommended setup:

- Install or enable the Python plugin.
- Configure Python SDK/interpreter as `.venv`.
- Run `src/generate_report.py` or the `generate-health-report` script.

Clean generated files:

```powershell
Remove-Item -Recurse -Force output, figures, data\processed
```
