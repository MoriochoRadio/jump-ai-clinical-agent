# Scenario 001 JSON Fixture Review

## Purpose

Check whether `prototype/inputs/scenario_001.json` matches the source scenario document.

Source:

- `experiments/scenario_001_type2_diabetes.md`

Fixture:

- `prototype/inputs/scenario_001.json`

## Review Result

Status: pass.

The JSON fixture preserves the core scenario content from the Markdown source and adds prototype metadata for repeatable workflow execution.

## Matched Fields

| Source Section | JSON Location | Status |
| --- | --- | --- |
| Disease / Condition | `required_fields.disease_condition` | matched |
| Intervention Or Drug Class | `required_fields.intervention_or_drug_class` | matched |
| Trial Phase | `required_fields.trial_phase` | matched |
| Trial Objective | `required_fields.trial_objective` | matched |
| Target Population | `required_fields.target_population` | matched |
| Draft Inclusion Criteria | `required_fields.draft_inclusion_criteria` | matched |
| Draft Exclusion Criteria | `required_fields.draft_exclusion_criteria` | matched |
| Primary Endpoint | `required_fields.primary_endpoint` | matched |
| Secondary Endpoints | `required_fields.secondary_endpoints` | matched |
| Expected Data Collection Items | `required_fields.expected_data_collection_items` | matched |
| Recruitment Assumption | `optional_fields.recruitment_assumption` | matched |
| Hospital Data Availability Notes | `optional_fields.hospital_data_availability_notes` | matched |
| Similar Trial NCT IDs | `optional_fields.similar_trial_nct_ids` | matched as empty list |
| Known Concerns | `optional_fields.known_concerns` | matched |
| Expected Agent Checks | `expected_agent_checks` | matched and structured |
| Expected Failure Modes | `expected_failure_modes` | matched and structured |
| Rubric Reference | `evaluation.rubric_path` | matched |

## Intentional Additions

The JSON fixture adds:

- `schema_version`,
- `scenario_id`,
- `scenario_name`,
- `source_markdown`,
- `data_safety`,
- evaluation thresholds.

These additions are not new scenario facts. They are execution metadata for the prototype.

## Safety Check

The fixture states:

- no real patient data,
- no identifiable data,
- synthetic protocol outline only,
- allowed use is agent workflow testing and proposal evaluation.

This matches the project safety boundary.

## Current Decision

Use `prototype/inputs/scenario_001.json` as the first prototype input fixture.

If the Markdown scenario changes later, update this JSON fixture and repeat this review.
