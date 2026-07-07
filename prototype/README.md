# Prototype

This folder contains the first implementation area for the Clinical Trial Protocol Review Agent.

The first prototype should be command-line or notebook-style before any web UI. The goal is to create one traceable pre-review report and one score sheet for Scenario 001.

## Folder Structure

```text
prototype/
  inputs/
    scenario_001.json
  prompts/
    protocol_checklist.md
    trial_case_evidence.md
    hospital_data_readiness.md
    critic_safety.md
    final_report.md
  runs/
    README.md
```

## Current MVP Path

1. Read `prototype/inputs/scenario_001.json`.
2. Normalize the input.
3. Run checklist and hospital data-readiness checks.
4. Query or plan a ClinicalTrials.gov lookup.
5. Produce a draft pre-review report.
6. Run safety critic checks.
7. Save final report and score under `prototype/runs/`.

The first run plan is documented in:

- `prototype/runs/scenario_001_run_plan.md`

## Run Command

From the project root:

```powershell
python prototype/run_scenario.py --input prototype/inputs/scenario_001.json --run-id scenario_001_run_001
```

If the run folder already exists and should be regenerated:

```powershell
python prototype/run_scenario.py --input prototype/inputs/scenario_001.json --run-id scenario_001_run_001 --overwrite
```

To retrieve live public ClinicalTrials.gov records:

```powershell
python prototype/run_scenario.py --input prototype/inputs/scenario_001.json --run-id scenario_001_run_001 --overwrite --fetch-sources
```

The live retrieval path uses an expanded query set:

- baseline drug class query: `GLP-1 receptor agonist`
- representative drug queries: `semaglutide`, `liraglutide`, `dulaglutide`, `exenatide`

Retrieved records are de-duplicated by NCT ID before relevance ranking.

The first deterministic run output is stored in:

- `prototype/runs/scenario_001_run_001/`

When `--fetch-sources` is used, the run also writes:

- `sources.json`
- `sources_ranked.json`
- `source_relevance_review.md`
- `top_trial_comparison.md`
- `data_readiness_table.md`

The reviewed Scenario 001 run also includes manual post-run review notes:

- `top_trial_interpretation_notes.md`
- `medical_plausibility_safety_review.md`

## Boundaries

The prototype must not:

- use real patient data,
- connect to real EMR/HIS systems,
- approve a protocol,
- claim regulatory compliance,
- make patient-specific medical recommendations,
- guarantee recruitment success.
