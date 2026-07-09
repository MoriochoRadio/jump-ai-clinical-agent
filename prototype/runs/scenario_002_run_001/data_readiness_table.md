# scenario_002 Hospital Data-Readiness Table

## Purpose

Summarize which protocol data elements are likely available from routine hospital systems and which require research-specific or manual collection.

This table is a planning aid for hospital information system, CRC, and study operations review. It does not claim access to real EMR/HIS data.

## Run Context

- run id: `scenario_002_run_001`
- scenario: NSCLC Phase II Immunotherapy Protocol Pre-Review
- total mapped items: 15
- high-risk items: 7
- items needing clarification: 11

## Data-Readiness Table

| Data Item | Likely Source Category | Collection Mode | Risk | Clarification Needed |
| --- | --- | --- | --- | --- |
| Demographics. | registration/demographic data | routine hospital system | low | no |
| Lung cancer diagnosis, stage, and histology. | diagnosis/problem list plus pathology report | mixed routine and manual | medium | yes |
| Molecular testing results such as EGFR, ALK, ROS1, and related actionable alt... | pathology or molecular laboratory result | mixed routine and manual | high | yes |
| PD-L1 expression result where available. | pathology or molecular laboratory result | mixed routine and manual | high | yes |
| ECOG performance status. | clinician assessment or oncology research form | mixed routine and manual | high | yes |
| Prior systemic therapy history. | unmapped or needs clarification | unknown | medium | yes |
| Concomitant medications including steroid or immunosuppressive therapy. | medication/order records plus manual reconciliation | mixed routine and manual | medium | yes |
| Baseline and follow-up CT imaging. | radiology report/images plus research response assessment | mixed routine and manual | high | yes |
| RECIST or tumor response assessment. | radiology report/images plus research response assessment | mixed routine and manual | high | yes |
| CBC, liver function, renal function, and thyroid laboratory results. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Infusion and treatment administration records. | medication administration or infusion records | routine hospital system | medium | no |
| Pregnancy test result where applicable. | laboratory results | routine hospital system or protocol-specific lab | medium | no |
| Informed consent documentation. | research consent documentation | research-only/manual | high | yes |
| Adverse events and immune-related adverse events. | research-specific adverse event capture plus clinical notes | research-only/manual plus notes | high | yes |
| Visit schedule and follow-up completion. | scheduling/visit records plus research tracking | mixed routine and manual | medium | yes |

## Operational Reading

- Low-risk routine items are likely available in registration, laboratory, vital sign, or diagnosis/order systems.
- Mixed-source items may require reconciliation between EMR/HIS records and research forms.
- Research-only or manual items require explicit workflow ownership, documentation location, and quality-control checks.
- Any real implementation must be validated against the actual hospital system configuration and study protocol.

## Current Decision

Use this table to identify which protocol fields need EMR/HIS mapping versus research-specific documentation planning.
