# scenario_002 Source Relevance Review

## Purpose

Review whether retrieved ClinicalTrials.gov records are relevant enough to support similar-trial comparison.

Input source file:

- `prototype/runs/scenario_002_run_001/sources.json`

Ranked source file:

- `prototype/runs/scenario_002_run_001/sources_ranked.json`

## Scenario Target

- condition: Advanced or metastatic non-small cell lung cancer
- intervention: PD-1/PD-L1 immune checkpoint inhibitor add-on therapy
- phase: Phase II
- primary endpoint: Progression-free survival.

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
| 1 | `NCT02846792` | high | 10/10 | direct intervention or representative term match |
| 2 | `NCT04105270` | high | 10/10 | direct intervention or representative term match |
| 3 | `NCT04691817` | high | 10/10 | direct intervention or representative term match |
| 4 | `NCT04984811` | high | 10/10 | direct intervention or representative term match |
| 5 | `NCT05344209` | high | 10/10 | direct intervention or representative term match |
| 6 | `NCT05941897` | high | 10/10 | direct intervention or representative term match |
| 7 | `NCT06388031` | high | 10/10 | direct intervention or representative term match |
| 8 | `NCT02713867` | high | 9/10 | direct intervention or representative term match |
| 9 | `NCT03829436` | high | 9/10 | direct intervention or representative term match |
| 10 | `NCT04423029` | high | 9/10 | direct intervention or representative term match |
| 11 | `NCT04612751` | high | 9/10 | direct intervention or representative term match |
| 12 | `NCT05334329` | high | 9/10 | direct intervention or representative term match |
| 13 | `NCT05867121` | high | 9/10 | direct intervention or representative term match |
| 14 | `NCT06635824` | high | 9/10 | direct intervention or representative term match |
| 15 | `NCT06875310` | high | 9/10 | direct intervention or representative term match |
| 16 | `NCT02087423` | high | 8/10 | intervention term appears in title or eligibility context, but not as the extracted intervention |
| 17 | `NCT03556228` | high | 8/10 | direct intervention or representative term match |
| 18 | `NCT03673332` | high | 8/10 | direct intervention or representative term match |
| 19 | `NCT07218003` | high | 8/10 | direct intervention or representative term match |
| 20 | `NCT03170960` | high | 8/10 | direct intervention or representative term match |
| 21 | `NCT04916002` | medium | 7/10 | no clear intervention match |
| 22 | `NCT02454933` | medium | 7/10 | intervention term appears in title or eligibility context, but not as the extracted intervention |
| 23 | `NCT03911219` | medium | 6/10 | intervention term appears in title or eligibility context, but not as the extracted intervention |

## Overall Assessment

Retrieval status:

- success

Retrieved count:

- 23

Assessment:

- Retrieved records are useful comparison candidates, but they should not be treated as proof that the draft protocol is correct.
- Local ranking helps prevent broad or weak matches from appearing equally relevant.
- Current retrieval uses an expanded query set and de-duplicates records by NCT ID before ranking.

## Current Decision

Keep these retrieved records as comparison candidates.

Next recommended step:

- review whether the expanded query terms should be adjusted before adding the next scenario or publishing the run output.
