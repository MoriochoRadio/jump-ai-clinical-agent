# scenario_002 PubMed Manual Screening Notes

## Purpose

Record a conservative human-readable screening pass over the PubMed literature candidates generated for Scenario 002.

This file is not a clinical guideline review, systematic review, regulatory assessment, or expert oncology opinion. It is a portfolio trace showing how automated PubMed retrieval candidates are filtered before being used as support material.

## Screening Boundary

- Scenario: NSCLC Phase II Immunotherapy Protocol Pre-Review.
- Target use: support protocol pre-review questions about trial design, eligibility, endpoints, biomarker handling, and safety monitoring.
- Source files:
  - `prototype/runs/scenario_002_run_001/pubmed_sources.json`
  - `prototype/runs/scenario_002_run_001/pubmed_relevance_review.md`
- Full abstract text is not stored in this repository.
- Decisions below should be reviewed by a clinical or oncology research expert before being cited as substantive medical evidence.

## Decision Categories

- `primary_support_candidate`: closely aligned with NSCLC immunotherapy and useful for endpoint, eligibility, biomarker, safety, or protocol-comparison context.
- `context_only`: useful background, but population, treatment setting, phase, or cancer type differs from the Scenario 002 draft.
- `exclude_from_direct_support`: not suitable as direct support for this scenario; may remain only as a retrieval-quality example.

## Manual Screening Table

| PMID | Auto Score | Auto Decision | Manual Decision | Rationale | Suggested Use |
| --- | ---: | --- | --- | --- | --- |
| `38127362` | 10/10 | high_priority_screen | primary_support_candidate | Metastatic nonsquamous NSCLC and atezolizumab-containing randomized clinical trial context are closely aligned with the scenario's immunotherapy comparison needs. | Compare treatment context, endpoints, safety monitoring, and eligibility structure. |
| `27718847` | 9/10 | high_priority_screen | primary_support_candidate | Directly relevant PD-L1-positive NSCLC pembrolizumab trial; useful for biomarker and eligibility review. | Support follow-up questions on PD-L1 rules, prior therapy, endpoints, and safety capture. |
| `29658856` | 8/10 | high_priority_screen | primary_support_candidate | Metastatic NSCLC pembrolizumab plus chemotherapy trial; aligned with immunotherapy-plus-background-treatment protocol comparison. | Compare metastatic NSCLC endpoint framing and safety/AE monitoring expectations. |
| `30280635` | 8/10 | high_priority_screen | primary_support_candidate | Squamous NSCLC pembrolizumab plus chemotherapy trial; relevant but subtype-specific. | Use as a subtype-aware comparator, not as a universal NSCLC template. |
| `33894335` | 8/10 | high_priority_screen | primary_support_candidate | Protocol-specified final analysis from KEYNOTE-189 in metastatic nonsquamous NSCLC; highly useful for endpoint and analysis framing. | Compare PFS/OS/response endpoint language and follow-up assumptions. |
| `37478883` | 10/10 | high_priority_screen | context_only | NSCLC and immunotherapy signals are strong, but early-stage or isolated recurrence plus radiotherapy differs from advanced/metastatic systemic add-on therapy. | Use only as background for trial design and AE monitoring, not direct protocol support. |
| `39288781` | 10/10 | high_priority_screen | context_only | Pembrolizumab and NSCLC are relevant, but neoadjuvant early-stage setting differs from the scenario's advanced/metastatic protocol. | Use only for broader immunotherapy trial-design context. |
| `40454642` | 9/10 | high_priority_screen | context_only | Nivolumab lung cancer trial with OS signal, but neoadjuvant setting differs from Scenario 002. | Use cautiously for endpoint vocabulary only. |
| `38101437` | 8/10 | high_priority_screen | context_only | NSCLC and EGFR eligibility are relevant, but the intervention is targeted therapy rather than PD-1/PD-L1 checkpoint therapy. | Use for biomarker/EGFR eligibility handling, not immunotherapy efficacy or safety support. |
| `39270695` | 6/10 | medium_priority_screen | context_only | NSCLC eligibility and phase signals are useful, but MET-targeted therapy differs from checkpoint-inhibitor intervention. | Use only for molecular eligibility and operational trial-design comparison. |
| `34102137` | 6/10 | safety_background_candidate | exclude_from_direct_support | Nivolumab and safety signals are present, but cancer type differs from NSCLC. | Do not use as Scenario 002 support except as a retrieval false-positive/background example. |
| `25891173` | 4/10 | safety_background_candidate | exclude_from_direct_support | Pembrolizumab checkpoint therapy is relevant, but melanoma population is outside the scenario. | Exclude from direct support. |
| `26027431` | 4/10 | safety_background_candidate | exclude_from_direct_support | Nivolumab checkpoint therapy is relevant, but melanoma population is outside the scenario. | Exclude from direct support. |
| `34986285` | 4/10 | safety_background_candidate | exclude_from_direct_support | Nivolumab/immune checkpoint signal is relevant, but melanoma population is outside the scenario. | Exclude from direct support. |

## Screening Summary

- primary support candidates: 5
- context-only candidates: 5
- excluded from direct support: 4

The automated abstract-screening step is useful for surfacing candidate records, but it over-prioritizes some articles with strong immunotherapy terms but mismatched population or treatment setting. Manual review is still required before treating any candidate as evidence.

## Implications For The Agent

- The agent should separate `retrieved`, `screened`, and `accepted for support` states.
- Literature candidates should not be cited as support until they pass a manual or expert review step.
- Direct NSCLC immunotherapy records should be prioritized over general checkpoint-inhibitor safety records from other cancers.
- Biomarker/eligibility records from non-checkpoint or targeted therapy trials can be useful operational comparators but should be labeled as context-only.

## Next Recommended Step

Add a compact `accepted_literature_candidates` section to future report generation so the final report can distinguish direct-support candidates from context-only or excluded records.
