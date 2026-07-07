# Scenario 001 Source Relevance Review

## Purpose

Review whether retrieved ClinicalTrials.gov records are relevant enough to support similar-trial comparison.

Input source file:

- `prototype/runs/scenario_001_run_001/sources.json`

Ranked source file:

- `prototype/runs/scenario_001_run_001/sources_ranked.json`

## Scenario Target

- condition: Type 2 diabetes mellitus
- intervention: GLP-1 receptor agonist add-on therapy
- phase: Phase II
- primary endpoint: Change in HbA1c from baseline to week 24.

## Relevance Scoring Method

Each retrieved study is scored on a 10-point scale:

| Dimension | Max Points |
| --- | ---: |
| Condition match | 2 |
| Intervention match | 3 |
| Phase match | 2 |
| Endpoint match | 2 |
| Eligibility usefulness | 1 |

Interpretation:

- 8-10: high relevance,
- 5-7: medium relevance,
- 1-4: low relevance,
- 0: not useful for comparison.

## Ranked Retrieved Records

| Rank | NCT ID | Relevance | Score | Main Reason |
| ---: | --- | --- | ---: | --- |
| 1 | `NCT01596504` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 2 | `NCT05067621` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 3 | `NCT01117350` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 4 | `NCT01373450` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 5 | `NCT02449603` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 6 | `NCT03015220` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 7 | `NCT05005741` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 8 | `NCT05407961` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 9 | `NCT07662213` | high | 9/10 | direct GLP-1 receptor agonist or representative drug match |
| 10 | `NCT02274740` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 11 | `NCT01542242` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 12 | `NCT01876849` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 13 | `NCT02981069` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 14 | `NCT06706284` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 15 | `NCT05473286` | high | 8/10 | direct GLP-1 receptor agonist or representative drug match |
| 16 | `NCT00630825` | medium | 7/10 | no clear GLP-1 intervention match |
| 17 | `NCT03648554` | medium | 7/10 | direct GLP-1 receptor agonist or representative drug match |
| 18 | `NCT04513704` | medium | 7/10 | direct GLP-1 receptor agonist or representative drug match |
| 19 | `NCT05073692` | medium | 7/10 | direct GLP-1 receptor agonist or representative drug match |
| 20 | `NCT06247748` | medium | 5/10 | no clear GLP-1 intervention match |
| 21 | `NCT06182852` | medium | 5/10 | GLP-1 appears in title or eligibility context, but not as the extracted intervention |

## Overall Assessment

Retrieval status:

- success

Retrieved count:

- 21

Assessment:

- Retrieved records are useful comparison candidates, but they should not be treated as proof that the draft protocol is correct.
- Local ranking helps prevent broad or weak matches from appearing equally relevant.
- Current retrieval uses an expanded query set and de-duplicates records by NCT ID before ranking.

## Current Decision

Keep these retrieved records as comparison candidates.

Next recommended step:

- use `top_trial_interpretation_notes.md` as the reviewer-facing interpretation layer before proposal writing.
