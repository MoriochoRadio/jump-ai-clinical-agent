# Project Artifact Inventory

## Current Location

The project artifacts are currently local.

Primary project folder:

- `C:\Users\neo62\Documents\Codex\2026-07-06\new-chat\work\jump-ai-clinical-agent`

Git status:

- local Git working tree exists,
- first local baseline commit has been created,
- GitHub remote is configured,
- baseline has been pushed to GitHub.

GitHub repository:

- https://github.com/MoriochoRadio/jump-ai-clinical-agent

## Main Artifact Groups

### Planning Documents

- `docs/00_project_brief.md`
- `docs/01_competition_analysis.md`
- `docs/02_career_fit.md`
- `docs/03_candidate_ideas.md`
- `docs/04_next_steps.md`
- `docs/05_working_protocol.md`
- `docs/06_decision_log.md`
- `docs/07_preliminary_vs_portfolio_strategy.md`
- `docs/08_problem_definition_validation.md`
- `docs/09_target_user_scenario.md`
- `docs/10_mvp_io_definition.md`
- `docs/11_mvp_agent_workflow.md`
- `docs/12_artifact_inventory.md`
- `docs/13_portfolio_improvement_plan.md`
- `docs/14_submission_record.md`
- `docs/15_post_submission_retrospective.md`
- `docs/16_seed_project_reference_analysis.md`

### Scenario And Evaluation Files

- `experiments/scenario_001_type2_diabetes.md`
- `experiments/scenario_001_rubric.md`
- `experiments/scenario_002_nsclc_immunotherapy.md`
- `experiments/scenario_002_rubric.md`

### Proposal Files

- `proposal/concept_note.md`
- `proposal/final_competition_review_ko.md`
- `proposal/hwpx_paste_ready_ko.md`
- `proposal/hwpx_paste_ready_plain_ko.txt`
- `proposal/proposal_draft_ko.md`
- `proposal/proposal_draft_scoring_review.md`
- `proposal/proposal_outline.md`
- `proposal/proposal_polishing_log.md`
- `proposal/proposal_revision_log.md`
- `proposal/rubric_mapping.md`
- `proposal/scenario_001_evaluation_alignment.md`
- `proposal/submission_form_condensed_ko.md`
- `proposal/submission_form_working_text_ko.md`
- `proposal/submission_format_decision.md`
- `proposal/submission_packaging_plan.md`
- `proposal/template_fields.md`

### Prototype Code

- `prototype/run_scenario.py`
- `prototype/inputs/scenario_001.json`
- `prototype/inputs/scenario_002.json`
- `tests/test_run_scenario.py`

### Submission Build Helper

- `scripts/build_submission_hwpx.py`
- `scripts/build_submission_docx.js`

Local-only generated submission draft:

- `proposal/MedIT_Agent_Lab_submission_draft.hwpx`
- `proposal/MedIT_Agent_Lab_submission_working.docx`

Generated submission files are ignored by Git. The final HWPX must be opened locally for visual page/layout verification before official submission.

### Scenario 001 Run Outputs

Primary run folder:

- `prototype/runs/scenario_001_run_001/`

Key outputs:

- `normalized_input.json`
- `checklist_findings.json`
- `data_readiness.json`
- `data_readiness_table.md`
- `source_plan.json`
- `sources.json`
- `sources_ranked.json`
- `source_relevance_review.md`
- `top_trial_comparison.md`
- `top_trial_interpretation_notes.md`
- `medical_plausibility_safety_review.md`
- `draft_report.md`
- `critic_review.md`
- `final_report.md`
- `score.md`

### Scenario 002 Run Outputs

Primary run folder:

- `prototype/runs/scenario_002_run_001/`

Key outputs:

- `normalized_input.json`
- `checklist_findings.json`
- `data_readiness.json`
- `data_readiness_table.md`
- `source_plan.json`
- `sources.json`
- `sources_ranked.json`
- `eligibility_criteria_extraction.json`
- `pubmed_plan.json`
- `pubmed_sources.json`
- `source_relevance_review.md`
- `pubmed_relevance_review.md`
- `pubmed_manual_screening.json`
- `pubmed_manual_screening_notes.md`
- `top_trial_comparison.md`
- `reviewer_summary.md`
- `draft_report.md`
- `critic_review.md`
- `final_report.md`
- `score.md`

### Research Notes

- `research/problem_definition_evidence_review.md`
- `research/source_backed_evidence_matrix.md`

## Temporary Files

Temporary test runs are stored under:

- `_scratch/`

This folder is ignored by Git and should not be treated as portfolio output.

## Current Repository State

Current state:

- project is versioned locally and pushed to GitHub,
- durable project artifacts are committed in the local Git repository,
- `origin` remote points to `https://github.com/MoriochoRadio/jump-ai-clinical-agent.git`,
- competition proposal was submitted on 2026-07-08,
- public post-submission record is tracked in `docs/14_submission_record.md`,
- Scenario 002 has been added as a cross-domain generalization check for an oncology immunotherapy protocol scenario,
- PubMed/NCBI E-utilities retrieval has been added as a second public evidence-source step with literature metadata candidates, abstract-screening signals, structured manual screening decisions, and accepted-literature grouping in generated reports,
- comparator trial eligibility extraction now captures screening signals such as ECOG, PD-L1 thresholds, RECIST, stage/extent, biomarker rules, safety exclusions, and endpoint timing,
- Scenario 002 now includes a concise reviewer-facing summary report for faster portfolio inspection,
- focused regression tests now cover reviewer summary generation and oncology eligibility criteria extraction.

Recommended next repository step:

- continue future steps through small normal commits,
- keep temporary files in `_scratch/`,
- do not commit private competition templates, credentials, final submitted files with private metadata, or real patient data.
