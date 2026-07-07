# Concept Note

## Working Title

Clinical Trial Protocol Review Agent

## Selected Field

Field 3: Regulatory response and intelligent clinical trial design.

## One-Line Summary

An agentic AI system that reviews early clinical trial protocol drafts by comparing them with public evidence, similar trial cases, guideline-style checkpoints, and hospital data readiness requirements.

## Problem

Clinical trial protocol planning requires repeated review of evidence, similar trials, eligibility criteria, safety considerations, endpoint definitions, recruitment assumptions, data collection items, and regulatory-style documentation requirements.

For researchers or clinical research teams, this process can be difficult because information is spread across literature, trial registries, protocol checklists, recruitment assumptions, and hospital data systems. In early planning, missing protocol components, unrealistic eligibility assumptions, or unclear data requirements can create downstream rework and quality risks.

This problem is connected to drug development because clinical trial design is a key bridge between candidate drugs and real-world evaluation. It is also connected to Medical IT because a protocol is only feasible when required data can be collected, managed, and audited through hospital information systems, EMR-like records, and clinical research workflows.

## Proposed Agent

The proposed system is not a general chatbot. It is a workflow-centered multi-agent reviewer.

Candidate agent roles:

- Evidence Agent: searches and summarizes public literature or background evidence.
- Trial Case Agent: compares the draft with similar clinical trial structures.
- Protocol Checklist Agent: checks core protocol components such as population, endpoints, eligibility criteria, safety monitoring, and visit/data schedule.
- Hospital Data Readiness Agent: maps required observations to hospital data categories and flags items that may be hard to collect from routine clinical systems.
- Critic Agent: reviews missing evidence, overclaims, inconsistent assumptions, and unsupported recommendations.

Current MVP implementation narrows this idea into a traceable source-backed workflow:

- read a structured synthetic protocol scenario,
- run deterministic protocol completeness and eligibility-risk checks,
- retrieve public ClinicalTrials.gov records with expanded GLP-1-related query terms,
- de-duplicate and locally rank retrieved trial records,
- generate a compact top-trial comparison table,
- manually review the top-ranked trial candidates,
- map required observations to broad hospital/research data categories,
- add a bounded medical plausibility and safety review,
- generate a final pre-review report and score sheet.

## Expected Output

For a given disease area, intervention concept, and draft protocol outline, the system produces:

- protocol completeness checklist,
- evidence and similar-trial summary,
- missing or ambiguous item list,
- hospital data readiness notes,
- guideline-style risk flags for expert review,
- traceable final review report.

## Target User And Scenario

The primary target user is a hospital clinical research support team, including clinical research coordinators and medical IT/data support staff, reviewing an early protocol draft before expert review.

Representative scenario:

- a hospital research team drafts a Phase II clinical trial protocol outline,
- the team wants to check whether core protocol sections are complete,
- eligibility and recruitment assumptions need pre-review,
- required observations need to be mapped to broad hospital data categories,
- issues should be summarized before PI, sponsor, IRB/regulatory, or data-team review.

The agent's output is a pre-review packet, not an approval decision.

## Why This Fits The Competition

The competition asks for an agentic AI that solves a problem in drug development. This concept focuses on the clinical trial design and review stage, where drug development work becomes operational and evidence must become a protocol that can be executed.

It fits the proposal template because:

- necessity: early protocol review affects trial feasibility, documentation quality, and downstream rework risk,
- originality: multiple agents collaborate with a critic loop rather than answering as a single chatbot,
- feasibility: it can begin with public sources, checklists, and small scenarios,
- evaluation: outputs can be scored with checklist coverage, citation correctness, and missing-item detection,
- demo: agent steps can be visualized as a transparent review trace,
- impact: better early review can reduce avoidable rework and improve documentation quality.

## Why This Fits Medical IT Career Goals

This direction shows understanding of:

- clinical research workflows,
- hospital data readiness,
- medical information systems,
- traceability and audit requirements,
- conservative AI use in healthcare settings.

It avoids making unsupported medical diagnosis, treatment, or regulatory approval claims. The agent is positioned as a planning and review assistant, not as a clinical decision-maker or regulatory authority.

## Early Evaluation Idea

Start with 3 synthetic or public-style protocol scenarios.

For each scenario, evaluate:

- whether required protocol sections are identified,
- whether missing items are flagged,
- whether cited evidence is relevant,
- whether hospital data requirements are realistic,
- whether the final report separates facts, assumptions, and limitations.

The first evaluation scenario and scoring rubric are documented separately:

- `experiments/scenario_001_type2_diabetes.md`
- `experiments/scenario_001_rubric.md`
- `proposal/scenario_001_evaluation_alignment.md`

The first source-backed prototype run is documented separately:

- `prototype/runs/scenario_001_run_001/final_report.md`
- `prototype/runs/scenario_001_run_001/score.md`
- `prototype/runs/scenario_001_run_001/medical_plausibility_safety_review.md`

The source-backed evidence matrix for proposal expansion is documented separately:

- `research/source_backed_evidence_matrix.md`

## MVP Input/Output Boundary

The first MVP should use a hybrid input:

- required structured fields for disease, intervention, phase, objective, population, eligibility criteria, endpoints, and expected data items,
- optional free-text notes for recruitment assumptions, hospital data availability, known similar trials, and known concerns.

The first output should be a 1-2 page structured pre-review report:

- review summary,
- protocol completeness checklist,
- similar-trial/evidence items to check,
- eligibility and recruitment flags,
- hospital data-readiness notes,
- missing or ambiguous items,
- assumptions, limitations, and expert follow-up questions.

The initial agent workflow is documented in:

- `docs/11_mvp_agent_workflow.md`

## Initial Scope Boundary

In the first phase, the system will not:

- train a new medical model,
- claim regulatory approval capability,
- make patient-specific medical decisions,
- access real patient data,
- replace expert clinical or regulatory review.

The first prototype demonstrates only a narrow review workflow with public or synthetic information.
