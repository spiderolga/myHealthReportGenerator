# Personal Weight Regulation Report Generator

This folder contains a reproducible report generator for the project:

**Body Composition Regulation After Successful Weight Loss - N-of-1 Case Study**

Current scope: Draft v0.6, Sprint 1 - Body Composition Analysis.

## Inputs

Place these files in `data/`:

- `Health_Analytics_Database_DailySummary.xlsx`
- `MyFitnessPal_parsed_data.xlsx` (reserved for Nutrition sprint)
- `events.csv`

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

- `output/Personal_Weight_Regulation_Model_v0.6.pdf`
- `output/body_composition_metrics.csv`
- `output/monthly_body_composition.csv`
- `output/phase_summary.csv`
- figures in `figures/`

## Notes

- Withings Fat Mass and Lean Mass are treated as trend-level metrics, not clinical-grade body composition measurement.
- DEXA is not reproduced in this Sprint.
- Garmin calories are not interpreted in Sprint 1.


## IntelliJ IDEA

Open this folder as a Python project.

Recommended setup:

- Install or enable the Python plugin.
- Configure Python SDK/interpreter as `.venv`.
- Run `src/generate_report.py` or the `generate-health-report` script.

Clean generated files:

```powershell
Remove-Item -Recurse -Force output, figures
```

## Changelog

### v0.6

- Redesigned Figure 4.5.
- Added compact right-side **Event reference** table.
- Restored full event/intervention names.
- Split the Event reference into Interventions, Clinical events, and Travel.
- Added distinct visual grammar: intervention bands, vertical event markers, and translucent travel areas.
- Switched project setup to Python packaging via `pyproject.toml`.
