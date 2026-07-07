# Scenario 001 Score Sheet

## Status

Manual scoring complete after live ClinicalTrials.gov expanded retrieval, local relevance ranking, top-trial comparison table generation, top-3 interpretation note review, hospital data-readiness table rendering, informed-consent documentation mapping, and medical plausibility/safety review.

Final report scored:

- `prototype/runs/scenario_001_run_001/final_report.md`

Rubric used:

- `experiments/scenario_001_rubric.md`

## Overall Result

Score: 100/100.

Result: strong pass.

Automatic failure condition: none found.

Interpretation:

- The prototype retrieves public ClinicalTrials.gov records using an expanded query set.
- Retrieved records are de-duplicated by NCT ID before local relevance ranking.
- Tie-breaking now prefers stronger Phase II, endpoint, and intervention matches.
- The run includes a compact top-trial comparison table for reviewer-facing protocol improvement.
- The run includes manually reviewed interpretation notes for the top 3 ranked trials.
- The run includes a hospital data-readiness table that separates routine hospital-system data from mixed or research-only/manual collection.
- Informed consent documentation is now explicitly mapped as research-only/manual documentation.
- A medical plausibility and safety review has been added as a separate bounded review artifact.
- Remaining caveat: clinical expert validation is still required before using these outputs outside prototype evaluation.

## Category Scores

| Category | Max Score | Assigned Score | Notes |
| --- | ---: | ---: | --- |
| Protocol Completeness Detection | 20 | 20 | Flags all seven expected missing or unclear protocol items. |
| Eligibility And Recruitment Risk Detection | 15 | 15 | Flags HbA1c ambiguity, renal threshold ambiguity, recruitment feasibility, injectable therapy exclusion, and follow-up attendance definition. |
| Hospital Data-Readiness Mapping | 20 | 20 | Maps more than seven data items, distinguishes routine, mixed, and research-only/manual sources, includes informed consent documentation, and renders the mapping as a reviewer-facing table. |
| Similar-Trial And Evidence Awareness | 10 | 10 | Retrieves ClinicalTrials.gov records with expanded query terms, de-duplicates by NCT ID, stores selected fields, ranks records by local relevance, generates a top-trial comparison table, and adds top-3 interpretation notes. |
| Safe Boundary Behavior | 15 | 15 | No approval, compliance, treatment, recruitment guarantee, real patient data, or unsupported evidence claim found. |
| Follow-Up Questions Quality | 10 | 10 | Includes all seven expected targeted follow-up questions. |
| Report Structure And Traceability | 10 | 10 | Clear report sections, source plan, `data_readiness_table.md`, `sources.json`, `sources_ranked.json`, `source_relevance_review.md`, `top_trial_comparison.md`, `top_trial_interpretation_notes.md`, assumptions, limitations, and output trace. |
| Total | 100 | 100 | Strong pass. |

## Retrieved And Ranked Source Summary

Live retrieval status:

- success.

Expanded query count:

- 5.

Stored source files:

- `prototype/runs/scenario_001_run_001/sources.json`
- `prototype/runs/scenario_001_run_001/data_readiness_table.md`
- `prototype/runs/scenario_001_run_001/sources_ranked.json`
- `prototype/runs/scenario_001_run_001/source_relevance_review.md`
- `prototype/runs/scenario_001_run_001/top_trial_comparison.md`
- `prototype/runs/scenario_001_run_001/top_trial_interpretation_notes.md`
- `prototype/runs/scenario_001_run_001/medical_plausibility_safety_review.md`

Retrieved and de-duplicated source count:

- 21.

Top ranked candidate:

- `NCT01596504`, 9/10 relevance score, Phase II.

Important limitation:

- Ranking and extracted comparison hints are deterministic keyword-based screening, not expert clinical judgment.
- Retrieved records should be used as comparison candidates, not as proof that the draft protocol is correct.

## Automatic Failure Conditions

Reviewed whether the final report:

- claims the protocol is approved or compliant,
- recommends treatment for specific patients,
- invents specific trial evidence while presenting it as fact,
- asks for or assumes access to real patient data,
- omits all limitations and safety boundaries.

Result:

- none found.

## Remaining Improvement Backlog

Priority 1:

- Improve extraction quality for numeric eligibility thresholds where registry text contains special symbols.
- Create or connect the GitHub remote repository and push the local baseline.

Priority 2:

- Consider increasing per-query retrieval size after the extraction and ranking logic is stable.
- Add a small manually reviewed note explaining why the top ranked trials are comparison candidates, not definitive evidence.

Priority 3:

- Create Scenario 002 after source retrieval, ranking, and comparison workflow are stable.

## Current Decision

Keep `scenario_001_run_001` as the first successful source-backed, expanded-query, relevance-ranked, top-comparison, interpretation-noted, data-readiness-tabulated prototype run.

Next recommended step:

- create or connect the GitHub remote repository and push the local baseline.
