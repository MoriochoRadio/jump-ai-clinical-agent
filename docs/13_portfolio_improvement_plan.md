# Portfolio Improvement Plan

## Purpose

Define the next GitHub-facing improvement after the first baseline push.

The repository now has a working local prototype, source-backed Scenario 001 outputs, and an initial GitHub baseline. The next step should make the project easier for an external reviewer to understand.

## Options Considered

### Option 1: Improve README And Add Architecture Diagram

Value:

- strongest immediate portfolio improvement,
- helps reviewers understand the problem, workflow, outputs, and boundaries quickly,
- does not change prototype behavior,
- low implementation risk.

Decision:

- selected.

### Option 2: Build A User Interface

Value:

- more visually impressive,
- useful for demo presentation.

Risk:

- adds frontend complexity before the source-backed workflow and proposal are fully mature,
- may distract from problem definition and evaluation.

Decision:

- defer.

### Option 3: Create Scenario 002

Value:

- improves evaluation coverage,
- shows the workflow is not overfit to one example.

Risk:

- requires another careful evidence and safety review cycle.

Decision:

- useful after the repository is easier to review.

## Selected Improvement

Update the repository README so that a GitHub visitor can quickly understand:

- what problem the project addresses,
- why the project fits Medical IT and drug-development workflow needs,
- what the current MVP does,
- how the agent workflow is structured,
- where the main outputs are,
- what safety boundaries are enforced,
- what the next steps are.

## Completed Changes

- README rewritten as a portfolio-facing project overview.
- Mermaid architecture diagram added.
- Key outputs table added.
- Run instructions added.
- Safety boundaries made explicit.
- Near-term roadmap clarified.
- Competition proposal submission status added after 2026-07-08 submission.
- Public submission record added in `docs/14_submission_record.md`.
- Post-submission retrospective added in `docs/15_post_submission_retrospective.md`.
- `seed-project` reference structure analyzed in `docs/16_seed_project_reference_analysis.md`.
- README adapted into a problem-first portfolio flow inspired by `seed-project`.

## Next Recommended Step

Scenario 002, reviewer summaries, regression tests, CI, and reviewer workflow diagrams have now been added.

The next recommended step is a minimal static reviewer dashboard for `scenario_002_run_001`. The dashboard should be read-only, use committed outputs, avoid patient-level workflows, and keep the CLI prototype as the source of truth.

Decision record:

- `docs/18_next_portfolio_improvement_decision.md`
