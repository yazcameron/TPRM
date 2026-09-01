# Pause rules

The orchestrator owns pauses. Specialists only return JSON that says a pause is needed.

## When to pause

| File | Audience | Phase |
|------|----------|-------|
| `vendor-clarification.html` | requester | 1 |
| `context-discrepancy.html` | requester | 2 |
| `vendor-materials-request.html` | vendor | 3 |
| `soc2-followup.html` | vendor | 4 |
| `ai-questionnaire-followup.html` | vendor | 4 |

Chat line (verbatim), substituting the filename and audience:

`[filename].html → confirm with [requester / vendor] before moving forward`

## How to pause

1. Write the follow-up JSON payload.
2. Render with `scripts/render_html.py followup`.
3. Publish the file to Google Drive in `{Vendor} / #{Zip}` per `references/drive-output.md`.
4. `engagement.py pause --file <filename> --audience requester|vendor`.
5. Tell the user the verbatim line, plus the Drive folder path. Stop. Do not start the next phase.

## How to resume

The human must confirm in chat (they spoke with the requester/vendor, or they accept the current answers). Then:

1. `engagement.py confirm --file <filename>`.
2. Incorporate any new answers into `inputs/` and `state.json`.
3. Re-run the phase that paused. Do not skip ahead.

If `state.json` `paused_on` is set, refuse to advance. Tell the user which file is waiting.

## Scope change

If products, integration depth, or data shared change after Phase 1, set `scope_changed: true` and restart Phase 1 with the updated information. Keep prior HTML in the engagement folder; do not delete it.
