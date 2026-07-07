# MVP Input/Output Definition

## Purpose

Define the smallest useful input and output for the first version of the agent.

This prevents the project from becoming a broad "clinical trial AI" and keeps the workflow testable.

## MVP Scope

The MVP is a pre-review assistant for an early clinical trial protocol outline.

It does not create a full protocol from scratch. It reviews a draft outline and returns a structured risk/checklist packet.

## Input Scope Options

### Option A: Free-Text Protocol Outline

The user pastes a rough protocol draft in free text.

Pros:

- realistic,
- flexible,
- good for demo.

Cons:

- harder to evaluate consistently,
- may require complex parsing too early.

### Option B: Structured Form Input

The user fills a small structured form.

Pros:

- easiest to evaluate,
- good for a first prototype,
- keeps the workflow narrow,
- allows clear missing-field checks.

Cons:

- less realistic than messy real drafts.

### Option C: Hybrid Input

The user fills required structured fields and may add optional free-text notes.

Pros:

- practical balance,
- supports deterministic checks,
- still feels realistic.

Cons:

- slightly more complex than a pure form.

## Recommendation

Start with Option C: hybrid input.

This is the safest MVP design. Required fields make evaluation possible, while optional notes preserve realism.

## MVP Input Fields

### Required Fields

1. Disease / condition
   - Example: type 2 diabetes, rheumatoid arthritis, non-small cell lung cancer.

2. Intervention or drug class
   - Example: GLP-1 receptor agonist, JAK inhibitor, immune checkpoint inhibitor.

3. Trial phase
   - Example: Phase II.

4. Trial objective
   - One or two sentences describing what the trial wants to evaluate.

5. Target population
   - Age range, disease stage/severity, key patient group.

6. Draft inclusion criteria
   - Bullet list.

7. Draft exclusion criteria
   - Bullet list.

8. Primary endpoint
   - Main endpoint and approximate time frame.

9. Secondary endpoints
   - Bullet list.

10. Expected data collection items
    - Lab tests, imaging, questionnaire, adverse events, medication history, visit schedule, etc.

### Optional Fields

1. Recruitment assumption
   - Expected sample size, recruitment source, single-center/multicenter assumption.

2. Hospital data availability notes
   - What the team believes is available from EMR/HIS or research data capture.

3. Similar trial NCT IDs
   - Optional known ClinicalTrials.gov studies.

4. Known concerns
   - User-provided concerns or constraints.

## MVP Output Sections

### 1. Protocol Completeness Checklist

Purpose:

- check whether the required high-level sections are present.

Example outputs:

- present,
- missing,
- unclear,
- needs expert review.

### 2. Evidence And Similar-Trial Comparison Plan

Purpose:

- state what similar-trial evidence should be retrieved or compared.

MVP boundary:

- for the very first prototype, this may be a plan or a small ClinicalTrials.gov lookup, not a full literature review.

### 3. Eligibility And Recruitment Risk Flags

Purpose:

- identify eligibility criteria that may be too broad, too narrow, ambiguous, or hard to operationalize.

MVP boundary:

- the agent flags concerns for expert review; it does not decide whether criteria are scientifically correct.

### 4. Hospital Data-Readiness Notes

Purpose:

- map expected data collection items to broad hospital data categories.

Example categories:

- demographics,
- diagnosis/problem list,
- medication/orders,
- laboratory results,
- imaging,
- procedures,
- vital signs,
- adverse events,
- questionnaires/patient-reported outcomes,
- free-text clinical notes,
- manual research-only collection.

### 5. Missing Or Ambiguous Items

Purpose:

- list items that need clarification before expert review.

Examples:

- unclear endpoint time frame,
- no safety monitoring plan,
- eligibility criterion lacks threshold,
- required data item may require manual collection.

### 6. Assumptions And Limitations

Purpose:

- separate facts, assumptions, and limitations.

This is critical for safe healthcare AI positioning.

### 7. Expert Follow-Up Questions

Purpose:

- produce questions for PI, CRC, sponsor, IRB/regulatory expert, or hospital data team.

## Minimal Report Shape

The MVP report should fit on 1-2 pages.

Recommended structure:

```text
1. Review Summary
2. Completeness Checklist
3. Similar-Trial / Evidence Items To Check
4. Eligibility & Recruitment Flags
5. Hospital Data-Readiness Notes
6. Missing/Ambiguous Items
7. Assumptions, Limitations, Follow-Up Questions
```

## What The MVP Should Not Output

The MVP should not output:

- approval/rejection decision,
- final protocol,
- patient-specific recommendation,
- regulatory compliance certification,
- diagnosis or treatment recommendation,
- guaranteed recruitment estimate.

## First Test Scenario

Use a synthetic Phase II chronic disease protocol outline.

Recommended first scenario:

- condition: type 2 diabetes,
- intervention: GLP-1 receptor agonist add-on therapy,
- phase: Phase II,
- target population: adults with uncontrolled type 2 diabetes,
- endpoints: HbA1c change, weight change, adverse events,
- data items: demographics, HbA1c, weight/BMI, medication history, adverse events, visit schedule.

Why this scenario:

- common chronic disease,
- endpoints map naturally to hospital/lab data categories,
- similar public trials are likely available,
- medically familiar without being too niche.

The concrete first scenario is documented in:

- `experiments/scenario_001_type2_diabetes.md`

## Current Decision

Use hybrid input and a 1-2 page structured pre-review report.

This is the working MVP boundary before designing agent internals.
