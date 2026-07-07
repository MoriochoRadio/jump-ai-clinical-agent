# Prototype Runs

This folder will store traceable prototype run outputs.

Current plan:

- `scenario_001_run_plan.md`

Current run:

- `scenario_001_run_001/`

Recommended run folder shape:

```text
scenario_001_run_001/
  normalized_input.json
  sources.json
  draft_findings.json
  critic_review.md
  final_report.md
  score.md
```

Rules:

- keep run outputs reproducible,
- record sources queried,
- record limitations and safety checks,
- do not store real patient data.
