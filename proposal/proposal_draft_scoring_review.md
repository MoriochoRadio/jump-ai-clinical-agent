# Korean Proposal Draft Scoring Review

Date: 2026-07-07

Reviewed draft:

- `proposal/proposal_draft_ko.md`

Rubric reference:

- `proposal/rubric_mapping.md`
- `proposal/template_fields.md`

## Overall Assessment

Estimated preliminary score:

- 86 / 100

Interpretation:

- The draft is structurally strong and conservative.
- It clearly avoids unsafe clinical, regulatory, and patient-specific claims.
- The project is well aligned with Medical IT and clinical trial workflow.
- The main weaknesses are not concept quality but proposal competitiveness: impact quantification, evaluation scenario specificity, and implementation/demo detail need to be sharpened.

## Score By Criterion

| Criterion | Max | Estimated | Assessment |
| --- | ---: | ---: | --- |
| Necessity and problem definition | 20 | 18 | Strong problem framing with ICH, SPIRIT, recruitment, amendment, and EHR workflow evidence. Needs a slightly sharper "why now / who feels this pain" paragraph. |
| Originality and creativity of agent design | 20 | 18 | Multi-agent workflow, critic loop, traceability, and hospital data-readiness angle are clear. Needs more explicit autonomous planning/tool-selection behavior. |
| Technical feasibility | 20 | 18 | Strong because a CLI MVP already exists and uses public ClinicalTrials.gov retrieval. Needs a more concrete model/library/deployment stack for final-round build. |
| Evaluation set and metrics | 10 | 8 | Metrics are good and Scenario 001 exists. Scenario 002/003 remain TBD, and the 100/100 score needs careful framing to avoid looking self-serving. |
| Business and social value | 20 | 15 | Target users and value are plausible. Weakest section because expected time/cost impact is not quantified and before/after workflow is not concrete enough. |
| Research ethics and completeness | 10 | 9 | Strong safety boundaries. Needs an explicit AI-use disclosure, privacy boundary, and audit-log policy paragraph. |
| Total | 100 | 86 | Strong draft, but not yet submission-polished. |

## High-Priority Issues

### 1. Business And Social Value Is Underdeveloped

Current issue:

- The draft says the system can improve documentation quality and pre-review organization, but it does not show a clear before/after workflow.
- It avoids unsupported time/cost claims, which is good, but the section may look too cautious unless practical workflow value is made concrete.

Recommended fix:

- Add a before/after table:
  - current workflow: manual protocol reading, registry search, data availability discussion, safety boundary review,
  - proposed workflow: agent-generated issue list, source trace, data-readiness table, expert follow-up questions.
- Use conservative impact wording:
  - "expected to reduce repeated manual cross-checking,"
  - "expected to improve review readiness,"
  - "to be validated through scenario-based evaluation."

Do not write:

- "reduces IRB time by X%"
- "prevents amendments"
- "guarantees cost reduction"

### 2. Evaluation Set Needs Scenario 002 And Scenario 003 Definitions

Current issue:

- Scenario 001 is strong, but Scenario 002 and Scenario 003 are still TBD.
- Judges may see the evaluation plan as incomplete.

Recommended fix:

- Define two additional scenario concepts without fully implementing them yet:
  - Scenario 002: oncology or cardiovascular Phase II/III protocol with complex eligibility and safety monitoring,
  - Scenario 003: infectious disease or rare disease protocol with recruitment feasibility and data-readiness challenges.
- Add expected missing items for each scenario.

### 3. Technical Feasibility Needs Final-Round Stack

Current issue:

- The CLI MVP is real, but final-round demo implementation is described at a high level.

Recommended fix:

- Add a concrete final-round stack:
  - backend: Python CLI/service layer,
  - data retrieval: ClinicalTrials.gov API, NCBI E-utilities,
  - optional UI: Streamlit or lightweight React,
  - storage: local JSON/Markdown trace files,
  - evaluation: scenario rubric files and critic outputs.

### 4. Agent Autonomy Needs Clearer Tool-Use Logic

Current issue:

- The agent roles are clear, but the draft may still read like a deterministic pipeline.

Recommended fix:

- Add a short "planning and tool-selection" subsection:
  - if protocol lacks disease/intervention, stop and request clarification,
  - if disease/intervention exists, generate registry query,
  - if retrieved records are weak, broaden query terms,
  - if safety-critical terms appear, route to critic/safety review,
  - if data items are research-only/manual, flag data-readiness risk.

### 5. Ethics Section Needs Operational Policy

Current issue:

- Boundaries are strong, but operational policy is not explicit enough.

Recommended fix:

- Add:
  - no real patient data in MVP,
  - all outputs must include limitations,
  - all retrieved sources must be logged,
  - human expert review required before action,
  - no hidden clinical recommendation.

## Medium-Priority Issues

### 1. Korean Style Should Be Polished

Current issue:

- The draft intentionally keeps some English technical terms such as eligibility, readiness, workflow, trace.
- This is acceptable for planning, but final submission should be more polished.

Recommended fix:

- Decide consistent Korean/English mixed terminology:
  - eligibility -> 대상자 적격성 기준,
  - data readiness -> 데이터 수집 준비도,
  - traceability -> 추적 가능성,
  - workflow -> 업무 흐름.

### 2. References Need Submission-Ready Formatting

Current issue:

- References are listed, but not formatted uniformly.

Recommended fix:

- Convert to a consistent citation style with URL/PMID/DOI where available.

### 3. Team Name Is Still TBD

Current issue:

- Team name remains unresolved.

Recommended fix:

- Pick a simple professional team name before final formatting.

Candidate directions:

- MedIT Agent Lab
- Clinical AI Workflow Lab
- Protocol Intelligence Team

## Safe Phrases To Keep

Keep these positions:

- "pre-review support before expert review"
- "no real patient data"
- "not protocol approval or regulatory certification"
- "public sources and synthetic scenarios only"
- "traceable workflow with source, assumption, and limitation logs"

## Phrases To Avoid

Avoid these in the final submission:

- "reduces IRB review time"
- "prevents protocol amendments"
- "improves patient recruitment success rate"
- "automatically identifies real eligible patients"
- "certifies regulatory compliance"
- "automates clinical decision-making"

## Recommended Next Step

Revise `proposal/proposal_draft_ko.md` in this order:

1. Add before/after workflow and conservative value statement.
2. Define Scenario 002 and Scenario 003 at concept level.
3. Add final-round technical stack.
4. Add agent planning/tool-selection logic.
5. Add operational ethics and audit policy.
6. Polish Korean terminology.

Expected result after revision:

- estimated score can improve from 86/100 to around 91-94/100 without making unsafe claims.
