# Proposal Template Fields

Source:

- KHIDI public notice: https://www.khidi.or.kr/board/view?linkId=48946784&menuId=MENU01108
- Attachment: KHIDI proposal template HWPX file

Downloaded locally for analysis as `proposal/template.hwpx`.

The original template file is not intended to be committed to GitHub.

## Basic Metadata

The proposal form asks for:

- selected field: field 1, field 2, field 3, or field 4,
- team name,
- agent name,
- Korean keywords: up to 5,
- English keywords: up to 5,
- summary,
- total proposal length: within 10 pages.

## Main Sections

### 1. Necessity And Background Of Agent Use In Drug Development

Template guidance:

- clearly define the problem to solve in the drug development process,
- properly reflect domain knowledge such as pharmaceutical or chemical knowledge in the AI agent logic.

Our interpretation:

- This section must not start with the tool.
- It should start with a concrete workflow problem.
- For our Medical IT direction, this should connect drug development to clinical research, hospital data readiness, protocol planning, or regulatory review.

### 2. Agent Design, Originality, And Creativity

Template guidance:

- include autonomous planning and tool use beyond a simple chatbot,
- include differentiated architecture such as multi-agent collaboration or feedback loops.

Our interpretation:

- We need a clear agent workflow.
- The system should show planning, retrieval, checking, and revision.
- A critic/reviewer loop will likely be important.

### 3. Technical Feasibility

Template guidance:

- concrete plan for using open-source models or external libraries,
- realistic implementation under limited resources.

Our interpretation:

- Avoid claiming full-scale model training.
- Prefer public APIs, small prototypes, and auditable tool calls.
- Candidate tools may include PubMed, ClinicalTrials.gov, guideline documents, RDKit, PubChem, ChEMBL, or local checklists depending on final idea.

### 4. Agent Evaluation Appropriateness

Template guidance:

- define an appropriate evaluation set and evaluation metrics for agent performance.

Our interpretation:

- We need evaluation scenarios before building the demo.
- Possible metrics: checklist coverage, citation correctness, missing-item detection, hallucination/error flagging, human review rubric.

### 5. Final-Round Demo Scenario

Template guidance:

- explain how the agent will visualize the process of solving a complex problem step by step if selected for the final round.

Our interpretation:

- We should design a demo trace early.
- The demo should show agent steps, evidence sources, intermediate checks, and final report.
- This is a strong fit for a portfolio project.

### 6. Expected Impact Of Agent Adoption

Template guidance:

- expected time and cost reduction after solution adoption,
- practical applicability in pharmaceutical/biotech industry or research sites,
- expected impact on drug development process innovation and industrial competitiveness.

Our interpretation:

- Keep claims conservative.
- Tie impact to workflow efficiency, documentation quality, risk detection, and clinical research readiness.
- Avoid claiming direct clinical decision-making or validated medical outcome improvement.

## Immediate Implication

The template strongly supports our cautious direction:

> a narrow, workflow-centered agent with tool use, evaluation scenarios, and transparent demo steps.

The next decision should be selecting the proposal field and final problem direction.
