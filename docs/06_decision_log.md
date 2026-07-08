# Decision Log

This file records major decisions and options.

## Decision 001: How To Proceed After Reading The Proposal Template

Date: 2026-07-06

Status: accepted

### Context

The official proposal template has six main sections:

1. necessity and background,
2. agent design/originality,
3. technical feasibility,
4. evaluation appropriateness,
5. final-round demo scenario,
6. expected impact.

The template confirms that this is a proposal-and-agent-design competition, not a pure model-training leaderboard.

### Options

#### Option A: Field 3 - Regulatory And Intelligent Clinical Trial Design

Build around clinical trial protocol review, regulatory/guideline checklist support, and hospital data readiness.

Pros:

- strongest fit for Medical IT and hospital information system career goals,
- realistic without deep molecular modeling,
- directly maps to protocol, data, and regulatory workflows,
- easier to evaluate with checklists and sample scenarios.

Cons:

- must be careful to show drug-development relevance, not just hospital administration.

#### Option B: Field 4 - Converged Multi-Agent System

Build a broader system combining protocol review, evidence search, clinical feasibility, and limited drug repurposing hypothesis support.

Pros:

- more ambitious and differentiated,
- can include multiple agents and workflows.

Cons:

- higher risk of being too broad,
- harder to prove within 10 pages,
- can become less conservative.

#### Option C: Field 2 - Molecular Optimization Loop

Build around RDKit/PubChem/ChEMBL and molecule optimization.

Pros:

- very directly tied to drug development,
- clear use of chemistry libraries.

Cons:

- weaker fit for hospital information system career goals,
- requires stronger chemistry validation,
- higher risk of superficial results.

### Recommendation

Start with Option A.

Reason:

It is the most conservative and career-aligned path. It lets us show Medical IT thinking, clinical workflow understanding, agent design, evaluation planning, and practical implementation without overclaiming chemical or medical validation.

### Proposed Next Action

Write a one-page concept note for Option A before making any prototype.

### User Decision

The user accepted Option A and asked whether we should only prepare the preliminary proposal or also build the project regardless of final-round selection.

## Decision 002: Target User And Scenario

Date: 2026-07-06

Status: accepted as working direction

### Context

After validating the problem definition, the project needed a narrower target user. A broad "clinical trial agent" would be too vague and could drift away from the user's Medical IT career goals.

### Options

#### Option A: Hospital Clinical Research Coordinator / Clinical Research Support Team

Pros:

- strong Medical IT and hospital workflow fit,
- supported by EHR-based screening workflow evidence,
- naturally connects protocol criteria to hospital data readiness.

Cons:

- must keep drug development relevance explicit.

#### Option B: Principal Investigator / Clinical Researcher

Pros:

- strong protocol design fit,
- direct connection to study rationale and endpoints.

Cons:

- weaker hospital information system angle unless data readiness is emphasized.

#### Option C: Pharmaceutical Clinical Development Team

Pros:

- strongest drug development fit.

Cons:

- less aligned with hospital information system career positioning.

#### Option D: Hospital Research Data / Medical IT Support Unit

Pros:

- strongest HIS/data readiness fit.

Cons:

- can become too narrow or too far from the competition if not tied to protocol review.

### Recommendation

Use a combined primary target:

> Hospital clinical research support team, including CRC and medical IT/data support staff, reviewing early protocol drafts before expert review.

### Rationale

This target preserves both sides of the project:

- drug development relevance through clinical trial protocol design,
- Medical IT relevance through hospital data readiness and workflow integration.

## Decision 003: MVP Input/Output Boundary

Date: 2026-07-06

Status: accepted as working direction

### Context

After choosing the target user, the project needed a minimal input/output boundary before designing agent internals. Without a clear input and output, the agent architecture could become too broad.

### Options

#### Option A: Free-Text Protocol Outline

Pros:

- realistic,
- flexible,
- good for future demo.

Cons:

- harder to evaluate consistently,
- requires more parsing.

#### Option B: Structured Form Input

Pros:

- easiest to evaluate,
- narrow and deterministic.

Cons:

- less realistic than messy early drafts.

#### Option C: Hybrid Input

Pros:

- required fields make evaluation possible,
- optional notes keep realism,
- good balance for an MVP.

Cons:

- slightly more complex than pure structured input.

### Recommendation

Use Option C.

### Decision

The MVP will accept structured required fields plus optional free-text notes.

Required fields:

- disease/condition,
- intervention or drug class,
- trial phase,
- trial objective,
- target population,
- inclusion criteria,
- exclusion criteria,
- primary endpoint,
- secondary endpoints,
- expected data collection items.

Output:

- a 1-2 page structured pre-review report,
- no approval/rejection decision,
- no regulatory compliance certification,
- no patient-specific recommendation.

## Decision 004: First Synthetic Test Scenario

Date: 2026-07-06

Status: accepted as working scenario

### Context

The MVP needs a small test scenario before agent internals are designed. The scenario must be medically plausible, safe, and useful for evaluating the proposed output.

### Options Considered

#### Option A: Type 2 Diabetes / GLP-1 Receptor Agonist / Phase II

Pros:

- familiar chronic disease,
- endpoints map to common hospital data categories,
- likely has similar public trial records,
- useful for testing lab, medication, adverse event, and visit-data mapping.

Cons:

- must avoid treatment advice,
- must keep all data synthetic.

#### Option B: Rheumatoid Arthritis / JAK Inhibitor / Phase II

Pros:

- strong clinical trial pattern,
- eligibility and safety monitoring are rich.

Cons:

- more specialized safety/domain details.

#### Option C: Non-Small Cell Lung Cancer / Immunotherapy / Phase II

Pros:

- directly connected to complex oncology protocol amendment evidence.

Cons:

- higher domain complexity and risk of overclaiming.

### Recommendation

Use Option A for the first scenario.

### Decision

Scenario 001 is:

> Type 2 diabetes Phase II protocol pre-review for GLP-1 receptor agonist add-on therapy.

This scenario will be used to test missing-item detection, eligibility ambiguity detection, recruitment assumption flags, and hospital data-readiness mapping.

## Decision 005: Submission Packaging And Provisional Team Name

Date: 2026-07-08

Status: provisional working decision

### Context

The project now has a Korean proposal draft, source-backed evidence, a deterministic prototype, and a public GitHub repository. Before preparing the official competition submission file, the project needs a team-name placeholder and a clear rule for which artifacts are public portfolio materials versus private submission materials.

### Options

#### Option A: Use GitHub As The Public Portfolio Record And Keep Final Submission Files Local

Pros:

- avoids accidentally publishing private template files or personal information,
- keeps the repository useful for portfolio review,
- preserves a clear audit trail of decisions, evidence, prototype runs, and proposal drafts.

Cons:

- requires one extra local packaging step before submission.

#### Option B: Commit The Final HWPX/PDF Submission To GitHub

Pros:

- makes the final artifact easy to find from the repository.

Cons:

- higher risk of exposing private details,
- less flexible if the official template contains competition-specific or personal fields.

### Recommendation

Use Option A.

### Decision

The repository remains the public portfolio and reproducibility record. The official HWPX/HWP/PDF submission package stays local and ignored by Git unless a sanitized public copy is intentionally prepared later.

Provisional team name:

> MedIT Agent Lab

This name is career-aligned, short, and does not overclaim clinical or regulatory authority. It should be confirmed before the official submission file is prepared.
