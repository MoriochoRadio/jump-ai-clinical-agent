# Submission Packaging Plan

## Purpose

This document separates public portfolio materials from private competition submission files.

The project should remain useful as a GitHub portfolio even if the competition result is uncertain. At the same time, the actual submission package may include private template files, personal information, team information, or exported files that should not be committed without review.

## Provisional Team Name

Recommended provisional team name:

- MedIT Agent Lab

Reason:

- short and professional,
- clearly connected to Medical IT,
- broad enough to cover both hospital workflow and agent design,
- less overclaiming than names that imply certified regulatory or clinical authority.

Alternative names kept for later review:

- Clinical AI Workflow Lab
- Protocol Intelligence Team
- Hospital Trial Data Lab

Current decision:

- Use `MedIT Agent Lab` as a provisional name in the working proposal draft.
- Confirm the final team name before preparing the official submission file.

## Public GitHub Materials

Safe to keep in the public repository:

- project brief and decision logs,
- problem definition and source-backed evidence review,
- synthetic scenario files,
- prototype source code,
- generated reports from synthetic inputs,
- Korean proposal draft without private personal information,
- README and portfolio explanation.

Do not add real patient data, private sponsor data, credentials, personal contact information, or final competition submission files unless they have been explicitly reviewed and sanitized.

## Local Private Submission Materials

Keep these local unless intentionally reviewed for publication:

- official downloaded competition templates,
- filled HWPX/HWP submission forms,
- exported PDF submission copies,
- team member private information,
- any file containing personal contact details,
- final uploaded package or screenshots from the submission portal.

The repository `.gitignore` already excludes:

- `proposal/*.hwpx`
- `proposal/*.hwp`
- `proposal/*.pdf`
- extracted template text files under `proposal/`

## Recommended Final Packaging Route

1. Keep `proposal/proposal_draft_ko.md` as the source-controlled public draft.
2. Use the official template locally to create the final HWPX/HWP submission document.
3. Export a PDF locally for review and backup.
4. Check that the final document does not claim clinical approval, regulatory certification, or patient-specific decision support.
5. Submit the official file through the competition portal.
6. After submission, optionally create a sanitized public summary for GitHub if it does not expose private information.

## Current Packaging Decision

Recommended route:

- GitHub remains the portfolio and reproducibility record.
- Official HWPX/PDF submission files remain local and ignored by Git.
- The public proposal draft remains Markdown.
- Final team name and page-length fitting are handled immediately before official submission.

## Next Action

Confirm whether `MedIT Agent Lab` should become the final team name. If accepted, the next practical step is preparing the official local submission document from `proposal/proposal_draft_ko.md`.
