# Personal Weight Regulation Report Generator

This folder contains a reproducible report generator for the project:

**Body Composition Regulation After Successful Weight Loss - N-of-1 Case Study**

Current scope: Draft v0.4, Sprint 1 - Body Composition Analysis.

## Inputs

Place these files in `data/`:

- `Health_Analytics_Database_DailySummary.xlsx`
- `MyFitnessPal_parsed_data.xlsx` (reserved for Nutrition sprint)
- `events.csv`

## Run

```bash
python src/generate_report.py
```

## Outputs

- `output/Personal_Weight_Regulation_Model_v0.4.pdf`
- `output/body_composition_metrics.csv`
- `output/monthly_body_composition.csv`
- `output/phase_summary.csv`
- figures in `figures/`

## Notes

- Withings Fat Mass and Lean Mass are treated as trend-level metrics, not clinical-grade body composition measurement.
- DEXA is not reproduced in this Sprint.
- Garmin calories are not interpreted in Sprint 1.
