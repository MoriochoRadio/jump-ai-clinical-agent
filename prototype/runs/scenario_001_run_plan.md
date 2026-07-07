# Scenario 001 First Prototype Run Plan

## Purpose

Define the first traceable prototype run before writing implementation code.

The first run should prove that the workflow can take `prototype/inputs/scenario_001.json`, produce structured intermediate outputs, apply safety checks, and save a final pre-review report with a score sheet.

## Input

Primary input:

- `prototype/inputs/scenario_001.json`

Source scenario:

- `experiments/scenario_001_type2_diabetes.md`

Evaluation rubric:

- `experiments/scenario_001_rubric.md`

## Run ID

Use:

- `scenario_001_run_001`

Output folder:

- `prototype/runs/scenario_001_run_001/`

## Execution Options

### Option A: Manual Run

Description:

- read the JSON fixture manually,
- use prompts manually,
- save outputs by hand.

Pros:

- fastest,
- no code needed.

Cons:

- weak reproducibility,
- less useful for GitHub portfolio,
- hard to rerun consistently.

Decision:

- not recommended as the main path.

### Option B: Python CLI Run

Description:

- write a small Python script that reads the fixture and writes standardized run files.

Pros:

- reproducible,
- easy to version-control,
- easy to explain,
- suitable before building a UI.

Cons:

- requires minimal implementation.

Decision:

- recommended.

### Option C: Notebook Run

Description:

- use a Jupyter notebook to walk through each step.

Pros:

- good for explanation,
- useful for portfolio storytelling.

Cons:

- can become less clean as an executable workflow,
- harder to use as app logic later.

Decision:

- optional later companion, not the first implementation target.

## Selected Approach

Use Option B: Python CLI Run.

The first script should be small and deterministic. It should not call an LLM yet unless the local structure, source retrieval plan, and file outputs work.

## First Run Phases

### Phase 1: Input Load

Read:

- `prototype/inputs/scenario_001.json`

Write:

- `prototype/runs/scenario_001_run_001/normalized_input.json`

Checks:

- JSON is valid,
- required top-level fields exist,
- no real patient data flag is present,
- source Markdown and rubric paths are recorded.

### Phase 2: Deterministic Protocol Checks

Read:

- `normalized_input.json`

Write:

- `prototype/runs/scenario_001_run_001/checklist_findings.json`

Checks:

- required MVP fields present,
- ambiguous HbA1c threshold,
- ambiguous renal impairment threshold,
- missing study design details,
- missing sample size rationale,
- missing safety monitoring detail,
- unclear prior GLP-1 exposure handling,
- unclear adverse event workflow.

### Phase 3: Hospital Data-Readiness Mapping

Read:

- `normalized_input.json`

Write:

- `prototype/runs/scenario_001_run_001/data_readiness.json`

Checks:

- map expected data collection items to broad hospital/research categories,
- distinguish routine hospital-system data from research-only/manual capture,
- flag uncertain data availability.

### Phase 4: External Source Plan

Read:

- `normalized_input.json`

Write:

- `prototype/runs/scenario_001_run_001/source_plan.json`

MVP behavior:

- prepare a ClinicalTrials.gov API query plan,
- do not require live API retrieval in the first local run,
- record planned query terms.

Planned query concepts:

- condition: `Type 2 diabetes mellitus`
- intervention keyword: `GLP-1 receptor agonist`
- phase: `Phase 2`

Later extension:

- add actual ClinicalTrials.gov API retrieval,
- save retrieved trial IDs and selected fields in `sources.json`.

### Phase 5: Draft Report

Read:

- `normalized_input.json`
- `checklist_findings.json`
- `data_readiness.json`
- `source_plan.json`

Write:

- `prototype/runs/scenario_001_run_001/draft_report.md`

Required sections:

1. Review Summary
2. Protocol Completeness Checklist
3. Similar-Trial / Evidence Items To Check
4. Eligibility And Recruitment Flags
5. Hospital Data-Readiness Notes
6. Missing Or Ambiguous Items
7. Assumptions, Limitations, And Expert Follow-Up Questions

MVP behavior:

- first draft can be template-generated.
- LLM report generation may be added only after deterministic outputs are stable.

### Phase 6: Safety Critic

Read:

- `draft_report.md`

Write:

- `prototype/runs/scenario_001_run_001/critic_review.md`

Checks:

- no protocol approval claim,
- no regulatory compliance guarantee,
- no patient-specific treatment recommendation,
- no recruitment guarantee,
- no invented evidence,
- no request for real patient data,
- expert review required statement exists.

### Phase 7: Final Report

Read:

- `draft_report.md`
- `critic_review.md`

Write:

- `prototype/runs/scenario_001_run_001/final_report.md`

Rule:

- if the critic finds a blocking safety issue, do not create a final report until the issue is fixed.

### Phase 8: Score Sheet

Read:

- `final_report.md`
- `experiments/scenario_001_rubric.md`

Write:

- `prototype/runs/scenario_001_run_001/score.md`

MVP behavior:

- first score can be manually assigned using the rubric.
- later, semi-automated scoring can assist but should not replace human review.

## Expected Output Files

```text
prototype/runs/scenario_001_run_001/
  normalized_input.json
  checklist_findings.json
  data_readiness.json
  data_readiness_table.md
  source_plan.json
  sources.json
  sources_ranked.json
  source_relevance_review.md
  top_trial_comparison.md
  draft_report.md
  critic_review.md
  final_report.md
  score.md
```

Manual post-run review file:

```text
prototype/runs/scenario_001_run_001/
  top_trial_interpretation_notes.md
  medical_plausibility_safety_review.md
```

## Implementation Constraints

The first script should:

- use only local fixture data,
- write deterministic output files,
- avoid real patient data,
- avoid claiming clinical or regulatory authority,
- keep every output readable in GitHub,
- fail clearly if required fields are missing.

The first script should not:

- require an API key,
- require model training,
- require EMR/HIS access,
- require a web UI,
- silently overwrite completed run outputs without an explicit option.

## Success Criteria

The first run is successful if:

- the script reads `scenario_001.json`,
- the run folder is created,
- all expected files are written,
- safety critic output exists,
- final report includes explicit limitations,
- score sheet can be filled using the rubric.

## Current Decision

Current prototype status:

- standard-library Python CLI implemented,
- Scenario 001 deterministic run completed,
- live ClinicalTrials.gov retrieval added,
- local relevance ranking added for retrieved records,
- expanded query retrieval added for representative GLP-1 drug terms,
- retrieved records are de-duplicated by NCT ID before ranking,
- compact top-trial comparison table added,
- manually reviewed top-3 trial interpretation notes added,
- medical plausibility and safety review completed,
- hospital data-readiness table added,
- informed consent documentation added as explicit research-only/manual data item,
- final report and score sheet generated for `scenario_001_run_001`.

Current selected command:

```powershell
python prototype/run_scenario.py --input prototype/inputs/scenario_001.json --run-id scenario_001_run_001 --overwrite --fetch-sources
```

Next implementation target:

- create or connect the GitHub remote repository and push the local baseline.

Recommended review focus:

- keep `_scratch/` excluded,
- create a remote repository,
- push the current local baseline,
- continue future work through small traceable commits.
