# Post-Submission Retrospective

## Purpose

This document explains the project after proposal submission from a portfolio perspective.

The goal is to make the project understandable to a reviewer who wants to know:

- why this problem was selected,
- how the problem connects to Medical IT,
- what was actually implemented,
- how AI assistance was used,
- what safety boundaries were maintained,
- what should be built next.

## Why This Problem Was Selected

The selected problem is early clinical trial protocol pre-review.

This direction was chosen because it connects three areas:

- clinical trial design and documentation,
- hospital information and research data workflows,
- safe use of agentic AI before expert review.

The project intentionally avoids a broad "AI doctor" or "drug discovery model" claim. Instead, it focuses on a narrower workflow where AI can help organize information before a human expert makes decisions.

## Problem Definition

Early clinical trial protocol drafts must be reviewed across many dimensions:

- protocol completeness,
- eligibility criteria,
- recruitment assumptions,
- endpoint and safety monitoring details,
- similar public trial cases,
- hospital data availability,
- documentation and follow-up questions.

These checks are often distributed across PI, CRC, sponsor, IRB/regulatory, statistician, and Medical IT perspectives.

The project problem definition is:

> Can an agentic AI workflow help a hospital clinical research support team prepare a safer and more traceable protocol pre-review packet before expert review?

## Medical IT Fit

The project is relevant to Medical IT because it focuses on the operational bridge between clinical research documents and hospital data reality.

Examples:

- whether protocol data items are likely to exist in routine hospital systems,
- whether some items require research-only collection,
- whether eligibility criteria can be translated into structured data checks,
- whether protocol assumptions should trigger follow-up questions for PI, CRC, or data support staff.

This is not a direct EMR integration project yet. It is a pre-integration planning and review-support project.

## What Was Implemented Before Submission

At submission time, the project already included a reproducible MVP:

- standard-library Python CLI,
- synthetic Type 2 diabetes Phase II scenario,
- ClinicalTrials.gov retrieval,
- query expansion for GLP-1-related trials,
- local source de-duplication and ranking,
- protocol checklist findings,
- hospital data-readiness mapping,
- safety critic review,
- final pre-review report,
- manual rubric score,
- bounded medical plausibility and safety review.

The MVP is intentionally simple. It is designed to be auditable before it becomes visually impressive.

## How AI Assistance Was Used

AI assistance was used for:

- structuring the problem definition,
- comparing possible competition topics,
- drafting and revising proposal text,
- identifying evidence categories to verify,
- designing the agent workflow,
- writing and reviewing prototype code,
- checking proposal tone and safety boundaries.

AI outputs were not treated as final evidence by default. Public sources, competition materials, and generated artifacts were reviewed before being used in the final proposal.

## Safety Boundary

The project does not claim to:

- approve clinical trial protocols,
- certify regulatory compliance,
- replace PI, CRC, sponsor, IRB, statistician, regulatory, or clinical expert review,
- make patient-specific diagnosis or treatment recommendations,
- determine real patient eligibility,
- connect to real EMR/HIS systems,
- use real patient data,
- guarantee recruitment success.

This boundary should remain visible in the README, proposal notes, and future demo.

## What Worked Well

- The scope became specific enough to be credible.
- The project connects directly to Medical IT and hospital research support work.
- The MVP existed before submission, so the proposal was not only conceptual.
- Public and synthetic data boundaries reduced privacy and safety risk.
- The repository now contains a traceable history of decisions, drafts, and implementation outputs.

## Current Weak Points

- Scenario coverage is still narrow because only Scenario 001 is implemented.
- PubMed/NCBI retrieval is planned but not yet implemented as a working agent step.
- The current interface is CLI-only.
- Evaluation is still mostly scenario-based and manually reviewed.
- The repository needs a shorter portfolio narrative for external readers.

## Next Build Priorities

Recommended order:

1. Add Scenario 002 with a different clinical area.
2. Add PubMed/NCBI E-utilities retrieval as a documented evidence step.
3. Improve numeric eligibility and endpoint extraction.
4. Generate a cleaner reviewer-facing report from each run.
5. Add a small UI only after the CLI workflow remains reproducible.

The project should continue to prioritize traceability and safety over UI polish.
