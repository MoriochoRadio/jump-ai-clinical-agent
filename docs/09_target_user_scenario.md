# Target User And Scenario

## Purpose

This document narrows the project from a broad idea into a specific workflow.

The problem definition is now evidence-supported enough to move forward:

> Early clinical trial protocol drafts need a traceable pre-review process that checks completeness, evidence alignment, similar-trial patterns, recruitment/eligibility realism, and hospital data-readiness risks before expert review.

## Target User Options

### Option A: Hospital Clinical Research Coordinator / Clinical Research Support Team

Role:

- screens patients,
- coordinates study workflows,
- checks whether trial criteria and data collection plans are operationally realistic,
- communicates with investigators and sponsors.

Why it fits:

- strongest Medical IT and hospital workflow fit,
- supported by evidence that EHR-based screening can affect CRC workflow,
- connects naturally to EMR/HIS data readiness.

Risk:

- must still connect clearly to drug development, not just hospital administration.

### Option B: Principal Investigator / Clinical Researcher Drafting A Protocol

Role:

- defines study rationale, population, endpoints, and eligibility criteria,
- prepares early protocol draft before expert review.

Why it fits:

- strong protocol-design fit,
- clearly connected to clinical trial quality.

Risk:

- Medical IT angle may become weaker unless data readiness is emphasized.

### Option C: Pharmaceutical Clinical Development Team

Role:

- designs sponsor-side protocol strategy,
- reviews similar trials, feasibility, recruitment risks, and endpoint strategy.

Why it fits:

- strongest direct drug development fit.

Risk:

- less aligned with the user's hospital information system career direction.

### Option D: Hospital Research Data / Medical IT Support Unit

Role:

- maps required trial data items to hospital data systems,
- supports research data capture and governance,
- checks whether required observations are structured, extractable, or likely manual.

Why it fits:

- strongest hospital information system fit.

Risk:

- may seem too narrow or too far from drug development unless tied to protocol review.

## Recommendation

Use a combined primary target:

> Hospital clinical research support team, including CRC and medical IT/data support staff, reviewing early protocol drafts before expert review.

This is safer than choosing only one role because the proposed agent spans protocol review and hospital data readiness. It also allows the portfolio to show Medical IT relevance while keeping the competition's drug-development focus.

## Primary User Persona

Name:

- Clinical Research Operations Reviewer

Representative role:

- A hospital-based clinical research coordinator or research support staff member who helps investigators prepare and operationalize trial protocols.

Responsibilities:

- understand draft protocol requirements,
- identify missing or ambiguous protocol elements,
- check whether eligibility criteria look operationally realistic,
- consider whether required data can be captured from routine records or research data capture workflows,
- prepare issues for PI, sponsor, IRB/regulatory experts, or data teams.

Pain points:

- protocol information is spread across literature, trial registry examples, checklists, and hospital data assumptions,
- eligibility and outcome definitions may look scientifically reasonable but be difficult to operationalize,
- manual pre-review is repetitive and hard to document consistently,
- early missing items can create downstream rework.

## Representative Scenario

### Situation

A hospital research team is preparing an early Phase II clinical trial protocol outline for a drug or intervention in a chronic disease area.

The draft includes:

- disease area,
- intervention concept,
- target population,
- inclusion/exclusion criteria,
- primary and secondary endpoints,
- visit/data collection plan,
- rough recruitment assumptions.

Before expert review, the team wants a structured pre-review.

### Agent Input

The user provides:

- disease/condition,
- intervention or drug class,
- trial phase,
- draft objective,
- draft eligibility criteria,
- draft endpoints,
- expected data collection items,
- optional notes about hospital data availability.

### Agent Process

The agent:

1. checks required protocol sections against a protocol checklist,
2. searches or compares similar public trial records,
3. flags missing or ambiguous eligibility/endpoints/data items,
4. maps required observations to broad hospital data categories,
5. identifies recruitment/data-readiness risks,
6. produces a traceable review report for expert follow-up.

### Agent Output

The output is not an approval decision.

It is a pre-review packet containing:

- protocol completeness checklist,
- similar-trial comparison summary,
- missing or ambiguous items,
- recruitment/eligibility realism flags,
- hospital data-readiness notes,
- assumptions and limitations,
- issues to escalate to PI, sponsor, IRB/regulatory expert, or data team.

## Scope Boundary

The agent does not:

- approve protocols,
- replace PI, CRC, IRB, CRA, sponsor, or regulatory expert review,
- use real patient data in the first prototype,
- make patient-specific recommendations,
- guarantee recruitment success,
- guarantee regulatory compliance.

## Portfolio Value

This target user scenario shows:

- hospital workflow understanding,
- clinical research operations awareness,
- Medical IT/data readiness thinking,
- safe AI boundaries,
- traceable decision-support design.
