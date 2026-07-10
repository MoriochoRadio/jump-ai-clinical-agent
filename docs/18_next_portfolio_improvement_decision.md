# Next Portfolio Improvement Decision

## Purpose

Decide whether the next repository improvement should be:

- a small reviewer-facing UI, or
- a third clinical scenario.

This decision is for portfolio value and repository clarity, not for competition submission scoring.

## Current State

The repository already includes:

- a submitted competition proposal record,
- two synthetic clinical scenarios,
- public ClinicalTrials.gov retrieval,
- PubMed metadata retrieval and manual screening support,
- reviewer-facing summary output,
- scenario scoring,
- regression tests,
- GitHub Actions CI,
- reviewer workflow diagrams.

This means the next improvement should not simply add more volume. It should make the existing work easier to inspect.

## Option 1: Small Reviewer-Facing UI

Scope:

- static local page or lightweight app,
- no backend,
- no login,
- no real patient data,
- no live EMR/HIS connection,
- no new medical claims,
- links to committed scenario outputs.

Portfolio value:

- makes the project easier to understand in a demo,
- shows practical product and workflow thinking,
- helps non-technical reviewers inspect the generated packet,
- gives a clearer bridge between CLI output and hospital/research support use.

Risk:

- can distract from the core agent workflow if overbuilt,
- requires careful UI scope control,
- must avoid implying clinical approval or production readiness.

Risk control:

- build only a read-only reviewer dashboard,
- use existing committed outputs,
- keep the CLI as the source of truth,
- show safety boundaries on the first screen,
- avoid patient-level forms or treatment recommendation features.

## Option 2: Scenario 003

Scope:

- add another synthetic clinical domain,
- run the same workflow,
- score and document the result.

Portfolio value:

- provides additional generalization evidence,
- demonstrates repeatability across disease areas.

Risk:

- lower marginal value after Scenario 002,
- adds more documents for reviewers to read,
- requires another careful evidence and safety review cycle,
- may make the repository feel broad before the existing outputs are easy to navigate.

## Recommendation

Choose Option 1: small reviewer-facing UI.

Reason:

The project already has enough backend workflow evidence for the current portfolio stage. A third scenario would add coverage, but it would not solve the main remaining reviewer problem: the output packet is detailed but spread across multiple Markdown and JSON files.

A small read-only UI has higher immediate portfolio value because it can show:

- the problem framing,
- the selected scenario,
- major pre-review risks,
- public evidence trace,
- hospital data-readiness risks,
- safety boundaries,
- links to full reproducible artifacts.

## Selected Next Step

Build a minimal static reviewer dashboard for `scenario_002_run_001`.

Implementation status:

- completed as `dashboard/scenario_002_review.html`,
- guarded by a regression test in `tests/test_dashboard_artifact.py`.

Initial constraints:

- static HTML/CSS/JavaScript is enough,
- no framework unless the scope grows,
- no external package dependency,
- no network call from the UI,
- no patient data,
- no editing or submission workflow,
- no claims of clinical correctness.

Success criteria:

- a reviewer can understand the Scenario 002 run in under five minutes,
- the dashboard links back to the underlying Markdown/JSON artifacts,
- safety boundaries are visible without scrolling far,
- the repository remains runnable from the CLI and tested by CI.
