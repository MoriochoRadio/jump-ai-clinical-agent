# Submission Record

## Summary

The proposal for the 4th JUMP AI / AI drug development challenge was submitted on 2026-07-08.

This document records what was submitted and how it should be represented in the public portfolio repository.

## Submitted Direction

- Competition: 4th JUMP AI / AI drug development challenge
- Field: regulatory response and intelligent clinical trial design
- Team name: MedIT Agent Lab
- Agent name: Clinical Trial Protocol Review Agent
- Korean name: 임상시험 프로토콜 사전검토 에이전트

## Project Scope

The submitted proposal defines an agentic AI workflow for early clinical trial protocol pre-review.

The system is intended to help hospital clinical research and Medical IT support teams prepare a traceable pre-review packet before expert review.

The project focuses on:

- protocol completeness checks,
- similar public trial retrieval from ClinicalTrials.gov,
- eligibility and recruitment assumption review,
- hospital data-readiness mapping,
- safety and responsibility boundary checks,
- final pre-review report generation.

## Implemented MVP At Submission

At submission time, the repository already included a working standard-library Python CLI prototype.

Implemented Scenario 001:

- synthetic Type 2 diabetes Phase II protocol scenario,
- ClinicalTrials.gov retrieval,
- GLP-1-related query expansion,
- local source de-duplication and relevance ranking,
- top-trial comparison,
- hospital data-readiness mapping,
- safety critic review,
- final pre-review report,
- manual rubric scoring,
- bounded medical plausibility and safety review.

Primary runnable entry point:

```powershell
python prototype/run_scenario.py --input prototype/inputs/scenario_001.json --run-id scenario_001_run_001 --overwrite --fetch-sources
```

## Public Repository Boundary

The public repository should keep:

- reproducible source code,
- synthetic scenarios,
- public-source evidence notes,
- proposal support drafts,
- workflow and safety documentation,
- generated scenario outputs that contain no private or patient data.

The public repository should not keep:

- private downloaded competition templates,
- final submitted HWPX/PDF files if they contain private submission metadata,
- credentials,
- real patient data,
- real EMR/HIS exports,
- private sponsor data.

## Safety Position

The submitted project does not claim to:

- approve clinical trial protocols,
- certify regulatory compliance,
- replace PI, CRC, sponsor, IRB, statistician, regulatory, or clinical expert review,
- make patient-specific diagnosis or treatment recommendations,
- determine real patient eligibility,
- connect to real EMR/HIS systems,
- guarantee recruitment success.

This boundary is important for both healthcare safety and portfolio credibility.

## Post-Submission Portfolio Goal

The next portfolio goal is to make the repository understandable to an external reviewer in under five minutes.

The strongest next additions are:

- a concise retrospective explaining why this problem was selected,
- Scenario 002 to show the workflow generalizes beyond one disease area,
- PubMed/NCBI E-utilities retrieval as a documented evidence step,
- a small interface only after the CLI workflow remains reproducible.
