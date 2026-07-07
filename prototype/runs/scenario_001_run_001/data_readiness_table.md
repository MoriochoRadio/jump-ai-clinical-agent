# Scenario 001 Hospital Data-Readiness Table

## Purpose

Summarize which protocol data elements are likely available from routine hospital systems and which require research-specific or manual collection.

This table is a planning aid for hospital information system, CRC, and study operations review. It does not claim access to real EMR/HIS data.

## Run Context

- run id: `scenario_001_run_001`
- scenario: Type 2 Diabetes Phase II Protocol Pre-Review
- total mapped items: 12
- high-risk items: 2
- items needing clarification: 5

## Data-Readiness Table

| Data Item | Likely Source Category | Collection Mode | Risk | Clarification Needed |
| --- | --- | --- | --- | --- |
| Demographics. | registration/demographic data | routine hospital system | low | no |
| Diabetes diagnosis history. | diagnosis/problem list | routine hospital system | medium | no |
| Medication history. | medication/order records plus manual reconciliation | mixed routine and manual | medium | yes |
| HbA1c. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Fasting plasma glucose. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Body weight and BMI. | vitals or clinical measurements | routine hospital system | low | no |
| Renal function laboratory results. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Pregnancy test result where applicable. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Informed consent documentation. | research consent documentation | research-only/manual | high | yes |
| Adverse events. | research-specific adverse event capture plus clinical notes | research-only/manual plus notes | high | yes |
| Concomitant medications. | medication/order records plus manual reconciliation | mixed routine and manual | medium | yes |
| Visit schedule and follow-up completion. | scheduling/visit records plus research tracking | mixed routine and manual | medium | yes |

## Operational Reading

- Low-risk routine items are likely available in registration, laboratory, vital sign, or diagnosis/order systems.
- Mixed-source items may require reconciliation between EMR/HIS records and research forms.
- Research-only or manual items require explicit workflow ownership, documentation location, and quality-control checks.
- Any real implementation must be validated against the actual hospital system configuration and study protocol.

## Current Decision

Use this table to identify which protocol fields need EMR/HIS mapping versus research-specific documentation planning.
