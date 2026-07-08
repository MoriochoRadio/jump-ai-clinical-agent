# Submission Format Decision

## Decision

The official preliminary-round submission should remain HWPX.

Reason:

- The DAKER competition page states that preliminary participants submit the proposal as an `hwpx` file.
- The rules section also says the proposal is submitted through the competition website as an `hwpx` file.

## Practical Working Format

Use DOCX as the local editing format.

Reason:

- DOCX is easier to generate and inspect programmatically.
- Word-style editing is more stable than directly editing HWPX XML.
- The DOCX can be opened in Word, Hancom Office, or compatible editors for manual review.

## Final Route

Recommended workflow:

1. Generate `proposal/MedIT_Agent_Lab_submission_working.docx`.
2. Review wording, layout, and page count in a word processor.
3. Open the DOCX in Hancom Office or another HWPX-compatible editor.
4. Save/export as HWPX for official submission.
5. Recheck that the final HWPX is within 10 pages and contains no private information intended for GitHub.

## Repository Policy

Generated DOCX/HWPX/PDF submission files stay local and ignored by Git.

The repository keeps:

- Markdown source text,
- generation scripts,
- decision logs,
- portfolio-safe proposal drafts.
