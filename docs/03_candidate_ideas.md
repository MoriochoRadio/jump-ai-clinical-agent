# Candidate Ideas

This document will be updated before choosing a final proposal direction.

## Idea A: Clinical Trial Protocol Review Agent

### One-Line Summary

An agent that reviews a draft clinical trial protocol against public evidence, similar trials, and major guideline checkpoints.

### Why It Fits

- Strong link to hospital operations and clinical research.
- Fits Medical IT and HIS/data readiness.
- Easier to justify than molecule generation without a chemistry specialist.

### Possible Agents

- Literature Agent: retrieves disease and treatment evidence.
- Trial Search Agent: finds similar trials from ClinicalTrials.gov.
- Guideline Agent: checks ICH/FDA/MFDS-style protocol requirements.
- Data Readiness Agent: maps required variables to hospital/EMR-like data categories.
- Risk Critic Agent: flags feasibility, recruitment, safety, and missing criteria risks.

### Evaluation Sketch

- checklist coverage score,
- citation correctness,
- protocol missing-item detection,
- human-readable risk report quality,
- reproducibility on sample scenarios.

## Idea B: Hospital Data Readiness Agent For Drug Development Studies

### One-Line Summary

An agent that converts a drug-development or clinical study question into a hospital data collection plan.

### Why It Fits

- Very close to hospital information systems.
- Shows understanding of EMR/HIS, data fields, privacy, and workflow.

### Risk

Might look less directly like "drug development" unless connected clearly to clinical trial planning or real-world evidence.

## Idea C: Drug Repurposing Hypothesis Agent With Clinical Feasibility Check

### One-Line Summary

An agent that proposes drug repurposing hypotheses, then checks clinical trial feasibility and hospital data availability.

### Why It Fits

- Bridges drug development and Medical IT.
- More scientifically ambitious.

### Risk

Requires stronger biomedical validation and careful claims.

## Current Lean

Idea A is the safest and most strategically aligned starting point.
