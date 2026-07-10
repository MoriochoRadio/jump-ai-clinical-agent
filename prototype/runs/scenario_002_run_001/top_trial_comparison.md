# scenario_002 Top Trial Comparison

## Purpose

Compare the highest-ranked ClinicalTrials.gov records against the draft protocol review needs.

This file is a screening aid only. It does not prove clinical correctness, regulatory adequacy, or protocol approval.

## Draft Protocol Target

- condition: Advanced or metastatic non-small cell lung cancer
- intervention: PD-1/PD-L1 immune checkpoint inhibitor add-on therapy
- phase: Phase II
- primary endpoint: Progression-free survival.

## Top Ranked Trial Comparison

| Rank | NCT ID | Score | Phase | Intervention | Primary Endpoint | Eligibility Hint | Extracted Criteria | Safety/Exclusion Hints |
| ---: | --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | `NCT02846792` | 10/10 | PHASE1, PHASE2 | Nivolumab, Plinabulin | Maximum Tolerated Dose of Plinabulin and Nivolumab (Phase I); Up to 28 days | Patients with known activating mutations in epidermal growth factor receptor (EGFR), or known translocation in anaplastic lymphoma kinase (ALK) or ROS-1 are eligible p... | ECOG: performance status of 0; Timing: up to 16 months; Stage: stage IIIB, stage IV; Biomarker: mutations in epidermal growth factor receptor (EGFR), ALK) or ROS-1 are eligible provided they have progressed... | ecog, performance status, egfr, alk |
| 2 | `NCT02848651` | 10/10 | PHASE2 | Atezolizumab | Percentage of Participants With Objective Response Per Response Evaluation Criteria in Solid Tumors Version 1.1 (RECIST v1.1) as Determined by Investigator; Baseline u... | Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1 | ECOG: performance status of 0; RECIST: RECIST v1.1; Timing: up to 32 months; Stage: Stage IIIB, metastatic; Biomarker: PD-L1) test result by immunohistochemistry (IHC) are eligible for the study * Partici, P... | ecog, performance status, recist, measurable, pd-l1 |
| 3 | `NCT03023423` | 10/10 | PHASE1, PHASE2 | Atezolizumab, Daratumumab | Percentage of Participants With Overall Response Rate (ORR); Up to 1.5 years | Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1 | ECOG: performance status of 0; Stage: metastatic, Stage IIIb; Biomarker: PD-L1) score of tumor cells (TC)1-3 and immune cell PD-L1 score of tumor-infiltrating | ecog, performance status, recist, measurable, pd-l1 |
| 4 | `NCT03050060` | 10/10 | PHASE2 | Atezolizumab, Hypofractionated Radiation Therapy, Laboratory Biomarker Analysis, Nelfinavir Mesylate, Nivolumab | Response Rate; Up to 6 months after initiating treatment | Subjects must have measurable disease by Response Evaluation Criteria in Solid Tumors (RECIST) criteria independent of the lesion to be irradiated. | Timing: Up to 6 months, up to 2 years; Stage: stage IV, metastatic; Biomarker: PDL1 immune checkpoint inhibitor and nelfinavir as per standard of care * Ability | ecog, recist, measurable |
| 5 | `NCT04105270` | 10/10 | PHASE2 | Oral Restorative Microbiota Therapy (RMT) Capsules, Durvalumab 1500 mg IV, Cisplatin/pemetrexed or Carboplatin/pemetrexed, Placebo | Number of patients experiencing Progression Free Survival (PFS); 3 Years | Histologically or cytologically confirmed adenocarcinoma of the lung that is unresectable stage IIIB/C or stage IV, does not have an EGFR sensitizing (activating) muta... | RECIST: RECIST 1.1; Stage: unresectable, stage IIIB; Biomarker: EGFR sensitizing (activating) mutation or ALK or ROS1 translocation, mutation * Measurable disease based on RECIST 1 | recist, measurable, pd-l1, egfr, alk, ros1 |

## How To Use This Table

- Use the eligibility hints to decide whether the draft protocol needs more specific operational criteria.
- Use the safety/exclusion hints to check whether important exclusions, biomarkers, and monitoring rules need explicit definitions.
- Use endpoint timing to compare whether the draft endpoint time frame is plausible or materially different from similar trials.
- Treat every item as a comparison candidate that still needs clinical expert review.

## Current Decision

Keep this table as the compact reviewer-facing comparison view for scenario_002.

Structured extraction file:

- `prototype/runs/scenario_002_run_001/eligibility_criteria_extraction.json`
