# Source-Backed Evidence Matrix

Date: 2026-07-07

## Purpose

Collect credible sources that can support the proposal expansion for the Clinical Trial Protocol Review Agent.

This document separates:

- claims we can support,
- claims that require careful wording,
- claims we should avoid for now.

## Source Categories

### 1. Clinical Trial Quality And Protocol Completeness

Why this matters:

- The agent is positioned as a protocol pre-review tool.
- The proposal must show that protocol design, safety, data quality, and documentation completeness are real drug-development concerns.

Key sources:

| Source | Type | What It Supports | Proposal-Safe Claim |
| --- | --- | --- | --- |
| ICH E6(R3) Good Clinical Practice, final guideline, adopted 2025-01-06. URL: https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf | Official international guideline | Clinical trials should be designed and conducted to protect participants and produce reliable results; protocol appendices include design, participant selection, interventions, efficacy, safety, statistics, source records, quality control, ethics, and data handling. | Protocol pre-review can focus on completeness, safety, data handling, and quality-related questions before expert review. |
| SPIRIT-CONSORT website and SPIRIT 2025 materials. URL: https://www.consort-spirit.org/ | Reporting guideline organization | SPIRIT provides a structured checklist for randomized trial protocols; CONSORT/SPIRIT emphasize complete and transparent reporting. | A checklist-based protocol review is grounded in recognized trial protocol reporting expectations. |

Proposal-safe wording:

- "The project uses guideline-style checks inspired by recognized clinical trial protocol and GCP expectations."

Do not claim:

- "The agent certifies GCP compliance."
- "The agent performs regulatory review."

### 2. Public Trial Registry And Biomedical Retrieval

Why this matters:

- The prototype uses public trial registry data rather than private sponsor data.
- The proposal needs to justify similar-trial retrieval as technically feasible.

Key sources:

| Source | Type | What It Supports | Proposal-Safe Claim |
| --- | --- | --- | --- |
| ClinicalTrials.gov API documentation. URL: https://clinicaltrials.gov/data-api/about-api | Official public API documentation | ClinicalTrials.gov provides programmatic access to public study records. | Similar-trial lookup can begin with public ClinicalTrials.gov metadata. |
| ClinicalTrials.gov API v2 sample response. URL: https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes&pageSize=1&format=json | Official API response | Public records expose structured fields such as condition, study design, interventions, outcomes, eligibility criteria, contacts/locations, references, and IPD sharing information. | The prototype can retrieve and store structured public trial fields for traceable comparison. |
| NCBI E-utilities documentation. URL: https://www.ncbi.nlm.nih.gov/books/NBK25501/ | Official NCBI documentation | E-utilities provide a structured interface for searching and retrieving records from NCBI databases including biomedical literature. | PubMed evidence retrieval can be added later through an official structured API. |

Proposal-safe wording:

- "The MVP starts with public registry retrieval and can later extend to PubMed using NCBI E-utilities."

Do not claim:

- "ClinicalTrials.gov records prove that a draft protocol is clinically correct."

### 3. Recruitment And Eligibility Feasibility

Why this matters:

- The Scenario 001 agent flags eligibility ambiguity and recruitment feasibility risk.
- The proposal needs evidence that recruitment and eligibility are real operational issues.

Key sources:

| Source | Type | What It Supports | Proposal-Safe Claim |
| --- | --- | --- | --- |
| Treweek et al. "Strategies to improve recruitment to randomised trials." Cochrane Database of Systematic Reviews, 2018. PMID: 29468635. DOI: 10.1002/14651858.MR000013.pub6 | Systematic review | Recruiting participants to trials can be difficult; the review identified 68 eligible trials and 72 recruitment-strategy comparisons, but only a small number had high-certainty evidence. | Recruitment planning is a real and methodologically difficult clinical trial workflow problem. |
| Treweek et al. "Methods to improve recruitment to randomised controlled trials: Cochrane systematic review and meta-analysis." BMJ Open, 2013. PMID: 23396504. DOI: 10.1136/bmjopen-2012-002360 | Systematic review / meta-analysis | Some recruitment strategies showed promise, but many effects were unclear and ethical/methodological issues can arise. | Early protocol review should flag recruitment assumptions for expert review rather than guarantee recruitment success. |
| Botto, Smith, Getz. "New Benchmarks on Protocol Amendment Experience in Oncology Clinical Trials." Therapeutic Innovation & Regulatory Science, 2024. PMID: 38530628. DOI: 10.1007/s43441-024-00629-2 | Peer-reviewed industry benchmark study | Analysis of 950 protocols and 2,188 amendments found oncology protocols had higher amendment prevalence and amendment counts than non-oncology protocols; complex designs were associated with recruitment/retention barriers and amendments. | Avoidable protocol rework and amendments are recognized performance concerns in complex trials. |

Proposal-safe wording:

- "The agent flags recruitment and eligibility assumptions as issues for human feasibility review."

Do not claim:

- "The agent improves recruitment rates."
- "The agent prevents protocol amendments."

### 4. Hospital Data-Readiness And EHR-Based Trial Operations

Why this matters:

- The project is intentionally aligned with Medical IT and hospital information systems.
- The proposal must show that data mapping and EHR/research workflow integration are real concerns.

Key sources:

| Source | Type | What It Supports | Proposal-Safe Claim |
| --- | --- | --- | --- |
| Ni et al. "A Real-Time Automated Patient Screening System for Clinical Trials Eligibility in an Emergency Department: Design and Evaluation." JMIR Medical Informatics, 2019. PMID: 31342909. DOI: 10.2196/14185 | Peer-reviewed workflow evaluation | An EHR-based screening system integrated structured EHR data and unstructured narratives into clinical research coordinator workflow and reduced screening time in that setting. | EHR-based trial screening and research coordinator workflow support are real Medical IT use cases. |
| Raghavan et al. "How essential are unstructured clinical narratives and information fusion to clinical trial recruitment?" arXiv, 2015. URL: https://arxiv.org/abs/1502.04049 | Research preprint | Structured data alone was insufficient for many trial eligibility criteria in the studied cancer trial examples; unstructured narratives and temporal reasoning mattered. | Eligibility and data-readiness mapping can require more than simple structured field lookup. |
| Dobbins et al. "The Leaf Clinical Trials Corpus: a new resource for query generation from clinical trial eligibility criteria." arXiv, 2022. URL: https://arxiv.org/abs/2207.13757 | Research preprint / dataset paper | Translating clinical trial eligibility text into clinical database queries can be labor-intensive and error-prone, motivating structured annotation and NLP research. | Mapping free-text eligibility criteria to data queries is a legitimate Medical IT challenge. |

Proposal-safe wording:

- "The MVP does not access EHR data. It only maps protocol data needs to broad hospital/research data categories and flags uncertainty."

Do not claim:

- "The agent can determine real patient eligibility."
- "The agent is integrated with a hospital EMR."
- "The agent validates actual site feasibility."

### 5. Safe AI And Review-Boundary Positioning

Why this matters:

- The project is healthcare-adjacent and must avoid unsafe claims.
- The proposal should frame the agent as review support, not autonomous medical authority.

Key sources:

| Source | Type | What It Supports | Proposal-Safe Claim |
| --- | --- | --- | --- |
| WHO. "Ethics and governance of artificial intelligence for health." 2021. URL: https://www.who.int/publications/i/item/9789240029200 | WHO guidance | AI for health should put ethics and human rights at the center of design, deployment, and use, and governance should hold stakeholders accountable. | The system should be designed with explicit boundaries, accountability, and human expert review. |
| FDA. "Clinical Decision Support Software Guidance for Industry and FDA Staff." Content current as of 2026-01-29. URL: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software | Official FDA guidance | FDA distinguishes types of clinical decision support software and clarifies criteria for certain non-device CDS software functions. | The project should avoid patient-specific diagnostic/treatment claims and should preserve independent human review. |
| DailyMed Ozempic label, updated 2026-06-01. URL: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=adec4fd2-6858-4c99-91d4-531f5f2a2d79 | Official drug label source | GLP-1 receptor agonist safety topics include pancreatitis, hypoglycemia with insulin/secretagogues, acute kidney injury from volume depletion, severe gastrointestinal adverse reactions, gallbladder disease, pregnancy planning, and thyroid C-cell tumor risk. | Scenario-specific safety review should flag relevant safety considerations for clinical expert review. |

Proposal-safe wording:

- "The agent is a planning and review-support system. It does not make patient-specific medical recommendations."

Do not claim:

- "The agent is safe for clinical deployment."
- "The agent is FDA-cleared."
- "The agent can approve or reject a trial protocol."

## Evidence-To-Feature Mapping

| Prototype Feature | Evidence Base | Current Confidence |
| --- | --- | --- |
| Protocol completeness checklist | ICH E6(R3), SPIRIT 2025 | High |
| Similar trial retrieval | ClinicalTrials.gov API, local Scenario 001 API run | High for technical feasibility |
| PubMed retrieval roadmap | NCBI E-utilities | High for technical feasibility, not yet implemented |
| Recruitment/eligibility flags | Cochrane recruitment review, BMJ Open review, protocol amendment benchmark | Medium-high |
| Hospital data-readiness mapping | ICH data governance, Ni et al., Raghavan et al., Dobbins et al. | Medium-high |
| Safety critic boundaries | WHO AI ethics guidance, FDA CDS guidance, ICH E6(R3), DailyMed for scenario-specific drug safety | Medium-high |

## Proposal-Safe Problem Statement

Early clinical trial protocol drafts require repeated cross-checking across protocol structure, public evidence, similar trial records, eligibility and recruitment assumptions, safety considerations, and hospital data-readiness requirements. Recognized trial guidance and clinical research literature support that these are real workflow concerns. Therefore, a conservative agentic AI system can be positioned as a traceable pre-review assistant that prepares issues and evidence for human experts, without approving protocols, replacing regulatory review, or using real patient data.

## Claims To Avoid

- The agent reduces IRB review time.
- The agent guarantees protocol quality.
- The agent prevents protocol amendments.
- The agent improves patient outcomes.
- The agent identifies actual eligible patients.
- The agent integrates with a real EMR/HIS.
- The agent performs regulatory compliance certification.

## Next Evidence Gap

Still useful to collect later:

- clinical research data capture standards such as CDISC or EDC-related sources,
- trial feasibility assessment practice sources,
- Korean hospital/research-operation references if the proposal needs local context.
