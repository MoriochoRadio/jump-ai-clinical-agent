# Problem Definition Evidence Review

Date: 2026-07-06

## Research Question

Is our proposed problem real?

> Early clinical trial protocol planning requires repeated checks against evidence, trial design standards, similar trials, and data collection feasibility. Missing or inconsistent protocol elements can create downstream rework and quality risks.

## Short Answer

The core problem is source-backed.

The strongest evidence supports these claims:

- clinical trial design and protocol quality matter for participant safety, reliable results, and avoiding wasted resources,
- clinical trial protocols have recognized standard content/checklist expectations,
- protocol review must cover design, participants, interventions, outcomes, harms, recruitment, data sharing, and other structured elements,
- trial quality management includes data collection, data handling, data governance, audit trails, and computerized systems,
- public trial registries expose structured trial metadata that can support similar-trial comparison,
- eligibility and recruitment/data-readiness issues are real but need careful wording,
- recruitment is a recognized trial challenge,
- EHR-based screening can affect clinical research coordinator workflow,
- protocol amendments are common enough to be studied as a clinical trial performance issue.

## Source-Backed Claims

### Claim 1: Poorly designed or poorly conducted trials are a real quality and ethics problem.

Evidence:

- ICH E6(R3) states that well-designed and conducted clinical trials support drug development and healthcare decisions.
- It also states that trials with inadequate design and/or poor conduct may risk participant safety, yield unreliable results, be unethical, and waste resources.

Source:

- ICH E6(R3), Guideline for Good Clinical Practice, final version adopted 2025-01-06.
- URL: https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf

Evidence label: `Source-backed`

### Claim 2: Protocol content can be checked against established protocol reporting recommendations.

Evidence:

- SPIRIT-CONSORT describes SPIRIT as a minimum set of recommendations for reporting randomized trial protocols.
- The SPIRIT 2025 expanded checklist includes structured protocol items such as title, trial registration, roles, background/rationale, objectives, trial setting, eligibility criteria, interventions, outcomes, harms, participant timeline, sample size, and recruitment.

Sources:

- SPIRIT-CONSORT website: https://www.consort-spirit.org/
- SPIRIT 2025 expanded checklist PDF: https://www.consort-spirit.org/_files/ugd/b5740e_ffb985d849cc41afbe66d58babc8653f.pdf

Evidence label: `Source-backed`

### Claim 3: Data governance, metadata, audit trails, and computerized systems are part of clinical trial quality work.

Evidence:

- ICH E6(R3) includes data governance sections covering data capture, metadata including audit trails, data review, transfer/exchange/migration, retention/access, and computerized systems.
- ICH also frames quality management as including efficient protocol design and tools/procedures for trial conduct, including data collection and management.

Source:

- ICH E6(R3), sections on quality management and data governance.

Evidence label: `Source-backed`

### Claim 4: Similar-trial comparison is technically feasible using public trial registry data.

Evidence:

- A live ClinicalTrials.gov API sample returned structured fields including condition, study type, phase, design, enrollment, arms/interventions, primary outcomes, eligibility criteria, contacts/locations, references, and IPD sharing statement.

Source:

- ClinicalTrials.gov API v2 sample query: `https://clinicaltrials.gov/api/v2/studies?query.cond=diabetes&pageSize=1&format=json`

Evidence label: `Source-backed`

### Claim 5: Hospital/EHR data readiness is a legitimate issue, but our wording must stay careful.

Evidence:

- A clinical trial eligibility matching paper found that structured EHR data alone was insufficient for resolving many eligibility criteria in two cancer trial examples, with unstructured clinical narratives needed for a substantial share of criteria.
- This supports the idea that protocol criteria and hospital data availability/mapping can be nontrivial.

Source:

- Raghavan et al., "How essential are unstructured clinical narratives and information fusion to clinical trial recruitment?"
- URL: https://arxiv.org/abs/1502.04049

Evidence label: `Reasonable inference`

Caution:

- This is not direct evidence that our agent will reduce hospital workload.
- It only supports the narrower claim that eligibility/data mapping can require structured and unstructured clinical information.

### Claim 6: Recruitment is a recognized clinical trial challenge.

Evidence:

- A Cochrane review states that recruiting participants to trials can be extremely difficult.
- The review identified 68 eligible trials with more than 74,000 participants evaluating recruitment-improvement strategies.
- The review also found that only a small number of recruitment strategies had high-certainty evidence, suggesting recruitment is a real and methodologically difficult workflow problem.

Sources:

- Treweek et al., "Strategies to improve recruitment to randomised trials." Cochrane Database of Systematic Reviews, 2018.
- PubMed: https://pubmed.ncbi.nlm.nih.gov/29468635/
- BMJ Open abridged version: https://pubmed.ncbi.nlm.nih.gov/23396504/

Evidence label: `Source-backed`

Proposal-safe wording:

- "Recruitment planning is a known challenge in clinical trials, so early protocol review should flag unrealistic eligibility or recruitment assumptions for expert review."

### Claim 7: EHR-based screening is a real clinical research workflow, not just an imagined Medical IT angle.

Evidence:

- A JMIR Medical Informatics study integrated an automated clinical trial eligibility screening system into pediatric emergency department clinical research coordinator workflow.
- The system analyzed structured EHR data and unstructured narratives.
- Compared with manual screening, the study reported a 34% reduction in patient screening time and improvements in numbers screened, approached, and enrolled.

Source:

- Ni et al., "A Real-Time Automated Patient Screening System for Clinical Trials Eligibility in an Emergency Department: Design and Evaluation." JMIR Medical Informatics, 2019.
- PubMed: https://pubmed.ncbi.nlm.nih.gov/31342909/

Evidence label: `Source-backed`

Proposal-safe wording:

- "Hospital data and EHR-based screening workflows are relevant to clinical trial operations; our agent can flag whether protocol criteria appear mappable to routine data categories, without accessing real patient data."

### Claim 8: Protocol amendments are a real trial performance issue, especially in complex oncology trials.

Evidence:

- A 2024 Therapeutic Innovation & Regulatory Science study analyzed 950 protocols and 2,188 amendments from 16 drug development companies.
- In oncology protocols, amendments were more prevalent and more frequent than in non-oncology protocols.
- The authors conclude that increasingly complex designs are reflected in difficult-to-predict cycle times, barriers to recruitment and retention, and increased protocol amendments.

Source:

- Getz et al., "New Benchmarks on Protocol Amendment Experience in Oncology Clinical Trials." Therapeutic Innovation & Regulatory Science, 2024.
- PubMed: https://pubmed.ncbi.nlm.nih.gov/38530628/

Evidence label: `Source-backed`

Proposal-safe wording:

- "Avoidable protocol rework and amendments are a recognized performance concern in complex clinical trials; our system is positioned as an early pre-review tool, not as a guarantee that amendments will be prevented."

## Claims To Avoid For Now

### Do Not Claim: The agent reduces IRB approval time.

Reason:

- We have not yet found direct evidence for that specific effect.

Allowed safer wording:

- The agent may help identify missing or inconsistent protocol elements before expert review.

### Do Not Claim: The agent guarantees regulatory compliance.

Reason:

- Regulatory compliance requires expert and authority review.

Allowed safer wording:

- The agent provides guideline-style checklist support and flags items for expert review.

### Do Not Claim: The agent improves clinical outcomes.

Reason:

- No clinical validation exists.

Allowed safer wording:

- The agent supports planning, documentation quality, and traceable review.

## Revised Problem Definition

Clinical trial protocol planning requires teams to align scientific rationale, trial design, eligibility criteria, endpoints, safety monitoring, recruitment assumptions, data collection items, and documentation requirements. Authoritative guidance such as ICH E6(R3) and SPIRIT shows that these elements are central to trial quality, participant protection, and reliable results.

However, early-stage protocol drafts often require repeated cross-checking across multiple information sources: prior studies, trial registries, protocol checklists, recruitment assumptions, and data collection assumptions. For Medical IT and clinical research operations, a key risk is that required protocol criteria and observations may not be clearly mapped to hospital information systems, EHR-derived data categories, or research data capture workflows.

Therefore, a conservative and useful problem statement is:

> Early clinical trial protocol drafts need a traceable pre-review process that checks completeness, evidence alignment, similar-trial patterns, and hospital data-readiness risks before expert review.

This is a review-assistance and documentation-quality problem, not a clinical decision-making problem.

## Current Confidence

Problem existence:

- High for protocol completeness, quality, and data governance.

Medical IT relevance:

- High, supported by ICH data governance, ClinicalTrials.gov structured fields, and EHR-based eligibility screening literature.

Agentic AI fit:

- Medium-high. Still needs evaluation, but the workflow involves multi-source retrieval, checklist reasoning, similar-trial comparison, EHR/data-readiness reasoning, and critique.

Next evidence needed:

- source on clinical research data capture standards or EHR-to-trial interoperability,
- source on regulatory/guideline expectations for protocol review or data quality,
- source on trial feasibility assessment practices.
