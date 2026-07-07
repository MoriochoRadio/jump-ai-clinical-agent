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

## Next Recommended Step

Collect 5-10 credible sources supporting the workflow:

- clinical trial protocol quality and completeness,
- recruitment and eligibility feasibility,
- hospital data-readiness or EHR-based trial operations,
- public trial registry reuse,
- safe AI support boundaries in healthcare research workflows.
