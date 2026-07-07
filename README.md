# JUMP AI Clinical Agent

Portfolio-oriented project for the 4th JUMP AI / AI drug development challenge.

This repository documents the process of designing an agentic AI service aligned with Medical IT, hospital information systems, clinical data workflows, and healthcare operations.

## Project Direction

The competition asks:

> What problem in drug development does your agentic AI solve?

Our current direction is not to build a pure molecule-generation model first. Instead, we will explore a healthcare IT-oriented agent that supports clinical trial planning, regulatory review, hospital data readiness, and evidence-based decision support.

## Why This Fits My Career

Target career interests:

- Hospital information system operation and maintenance
- Healthcare data management
- Clinical workflow and medical IT systems
- AI-assisted healthcare service planning
- Reliable, auditable, regulation-aware software

This project will emphasize:

- Problem definition from a real healthcare workflow
- Agent architecture, not just a chatbot
- Use of public medical/drug/clinical sources
- Evaluation design and auditability
- GitHub-based process documentation

## Repository Structure

```text
docs/        Competition analysis, career fit, planning notes
proposal/    Proposal drafts and submission materials
research/    Literature, guidelines, data-source notes
experiments/ Small validation experiments and evaluation notes
prototype/   CLI prototype, scenario inputs, and traceable run outputs
```

## Current Status

Current stage: first source-backed MVP run completed locally.

Completed baseline work:

- selected a Medical IT-oriented clinical trial protocol review agent direction,
- documented competition fit and career fit,
- created Scenario 001 for a synthetic Type 2 diabetes Phase II protocol pre-review,
- implemented a standard-library Python CLI prototype,
- added live ClinicalTrials.gov retrieval with expanded GLP-1-related queries,
- generated deterministic checklist, hospital data-readiness, source-ranking, final-report, and score outputs,
- added manual top-trial interpretation notes,
- added a bounded medical plausibility and safety review.

Key current outputs:

- `proposal/concept_note.md`
- `prototype/run_scenario.py`
- `prototype/inputs/scenario_001.json`
- `prototype/runs/scenario_001_run_001/final_report.md`
- `prototype/runs/scenario_001_run_001/score.md`
- `prototype/runs/scenario_001_run_001/medical_plausibility_safety_review.md`

Current repository state:

- first local Git baseline commit created,
- GitHub remote repository connected and pushed,
- temporary scratch runs and private competition template extracts are excluded by `.gitignore`.

GitHub repository:

- https://github.com/MoriochoRadio/jump-ai-clinical-agent

Next goal: continue future work through small traceable commits.
