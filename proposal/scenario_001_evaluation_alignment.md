# Scenario 001 Evaluation Alignment

## Purpose

This document checks whether the Scenario 001 rubric supports the competition proposal evaluation criteria.

Scenario:

- `experiments/scenario_001_type2_diabetes.md`

Rubric:

- `experiments/scenario_001_rubric.md`

The main conclusion is that Scenario 001 is useful not only as a prototype test case, but also as proposal evidence. It shows that the project can define a realistic input, expected output, scoring method, and safety boundary before implementation.

## Alignment Summary

| Competition Criterion | Supported By Scenario 001? | Current Strength | Gap To Improve |
| --- | --- | --- | --- |
| Necessity and problem definition | Yes | Shows concrete early protocol review pain points: missing thresholds, unclear eligibility, data collection ambiguity, recruitment assumptions | Add 3-5 source-backed references in the proposal text |
| Originality and creativity of agent design | Partly | Rubric implies multiple review perspectives: protocol, evidence, data readiness, safety critic | Add explicit multi-agent workflow and critic loop diagram |
| Technical feasibility | Partly | Uses structured input and checklist-style output that can be implemented without model training | Define actual tools/APIs and a minimal prototype flow |
| Evaluation set and metrics | Strong | Provides 100-point scoring, expected findings, pass thresholds, and automatic failure conditions | Create 2-4 additional scenarios later |
| Business and social value | Yes | Focuses on reducing early rework and making hospital research review more traceable | Add conservative before/after workflow comparison |
| Research ethics and completeness | Strong | Includes safe boundary behavior and automatic failure conditions | Add AI-use disclosure and privacy statement to proposal |

## Detailed Mapping

### 1. Necessity And Problem Definition

Scenario 001 supports the problem definition because it turns an abstract issue into a concrete workflow problem.

It demonstrates that early protocol drafts can contain:

- incomplete eligibility thresholds,
- unclear exclusion criteria,
- missing study design details,
- weak recruitment assumptions,
- data collection items that may not map cleanly to routine hospital systems.

This helps avoid a vague "AI chatbot for clinical trials" framing.

Proposal use:

- use Scenario 001 as a short example in the necessity section,
- explain that the agent helps prepare a pre-review packet before PI, CRC, medical IT/data team, IRB, sponsor, or regulatory expert review.

### 2. Originality And Creativity Of Agent Design

The rubric separates agent output quality into different reasoning dimensions:

- protocol completeness,
- eligibility and recruitment risk,
- hospital data-readiness,
- similar-trial and evidence awareness,
- safety boundary behavior,
- follow-up question quality,
- traceable report structure.

This naturally supports a multi-agent design. Each dimension can map to a specialized internal role.

Possible proposal mapping:

| Rubric Area | Candidate Agent Role |
| --- | --- |
| Protocol Completeness Detection | Protocol Checklist Agent |
| Eligibility And Recruitment Risk Detection | Feasibility Review Agent |
| Hospital Data-Readiness Mapping | Hospital Data Readiness Agent |
| Similar-Trial And Evidence Awareness | Trial Case / Evidence Agent |
| Safe Boundary Behavior | Critic / Safety Agent |
| Follow-Up Questions Quality | Review Packet Agent |
| Report Structure And Traceability | Final Report Agent |

Gap:

- the proposal should include a simple architecture diagram showing this flow.

### 3. Technical Feasibility

Scenario 001 keeps implementation realistic because it does not require training a new medical model.

Feasible MVP implementation path:

1. Accept structured protocol fields.
2. Run rule/checklist-based checks for known missing elements.
3. Query public sources such as ClinicalTrials.gov for similar trial patterns.
4. Ask an LLM to draft a structured pre-review report.
5. Run a critic pass against safety and traceability rules.
6. Score the output with the rubric.

This supports technical feasibility because the first prototype can be built with:

- structured Markdown or JSON input,
- public APIs,
- prompt templates,
- deterministic checklist rules,
- human-readable scoring.

Gap:

- the tool/API list should be written before implementation starts.

### 4. Evaluation Set And Metrics

This is the strongest current alignment.

Scenario 001 already defines:

- a synthetic input,
- expected findings,
- 100-point scoring,
- pass and strong-pass thresholds,
- automatic failure conditions,
- hospital data-readiness expectations,
- safe boundary criteria.

This directly supports the proposal requirement for an evaluation set and metrics.

Gap:

- one scenario is not enough for a final evaluation plan.
- later, create at least three scenarios covering different trial patterns.

Suggested future scenario set:

| Scenario | Purpose |
| --- | --- |
| Type 2 diabetes Phase II | common chronic disease, lab/vitals/medication data mapping |
| Oncology Phase II | stricter eligibility, safety monitoring, imaging or biomarker complexity |
| Infectious disease or vaccine trial | visit schedule, adverse events, population criteria |
| Rare disease trial | recruitment feasibility and limited evidence challenge |

### 5. Business And Social Value

Scenario 001 shows practical value for hospital-facing clinical research support.

Potential value claims, stated conservatively:

- helps identify missing or ambiguous protocol items earlier,
- supports better preparation before expert review,
- makes hospital data collection assumptions more visible,
- improves traceability of early review comments,
- may reduce avoidable rework, but does not replace expert review.

Gap:

- avoid claiming exact time or cost savings unless supported by evidence.
- use wording such as "expected to reduce avoidable rework" instead of "will reduce review time by X%."

### 6. Research Ethics And Completeness

Scenario 001 strongly supports ethics and safety because the rubric includes automatic failure conditions.

Important boundaries:

- no protocol approval claim,
- no regulatory compliance guarantee,
- no patient-specific treatment recommendation,
- no real patient data,
- expert review remains required,
- assumptions must be separated from facts.

Proposal use:

- include these as an explicit safety policy,
- say that the agent is a planning and pre-review assistant,
- state that outputs are for expert review, not final decisions.

## Recommended Proposal Framing

In the proposal, Scenario 001 should be described as:

> A synthetic protocol pre-review scenario used to test whether the agent can detect missing protocol details, flag eligibility and recruitment risks, map expected observations to hospital data categories, maintain safe medical boundaries, and produce a traceable review packet.

This framing is stronger than saying:

> We will test whether the answer looks good.

## Current Decision

Keep Scenario 001 as the first evaluation scenario.

Do not expand to many scenarios yet. First, use this scenario to define the MVP workflow and tool chain, then create additional scenarios after the first dry run.

## Next Recommended Step

Define the MVP agent workflow:

1. input format,
2. agent roles,
3. tool/API candidates,
4. output report structure,
5. critic and scoring flow.

This should be done before writing code.
