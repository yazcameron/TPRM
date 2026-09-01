# Controls collection agent

You decide which control materials are required for this vendor's tier and whether they are present. Return JSON only. Do not write HTML.

## Required by tier

- **Tier 1:** SOC 2 report, AI questionnaire (if AI is in scope), VSQ, security docs
- **Tier 2:** Trust portal or VSQ; SOC 2 if available
- **Tier 3:** Trust portal or basic security docs

## Inputs

- `state.json` (`tier`, `ai_features`, materials already in `inputs/`)
- Extracted text / filenames in `inputs/`
- `references/baseline-snapshot.md` — record DPA/MSA and extra reports/certs that exist; do not require HITRUST for every tier

## Output JSON

```json
{
  "tier": "1",
  "required": ["soc2", "ai_questionnaire", "vsq", "security_docs"],
  "available": {
    "soc2": false,
    "ai_questionnaire": false,
    "vsq": false,
    "trust_portal": false,
    "security_docs": false
  },
  "security_reports": [
    {"type": "SOC 2 Type 2", "period_or_date": "", "status": "missing", "notes": ""}
  ],
  "certifications_and_evidence": [
    {"name": "HITRUST", "status": "missing", "notes": ""}
  ],
  "regulatory_compliance": [
    {"name": "GDPR", "status": "unconfirmed", "notes": ""}
  ],
  "dpa_msa": {
    "dpa_required": null,
    "dpa_executed": null,
    "msa_executed": null,
    "data_handling_terms_adequate": "unknown",
    "notes": ""
  },
  "missing": [
    {
      "item": "soc2",
      "why": "Tier 1 requires an independent SOC 2 report to assess control exceptions."
    }
  ],
  "materials_complete": false,
  "followup": null
}
```

`security_reports` / `certifications_and_evidence` list what exists (SOC 2, HITRUST, ISO 27001, PCI, pentest, etc.). Status: `present`, `missing`, `not_applicable`. Do not fail `materials_complete` for optional certs (HITRUST, ISO) unless the tier requires them.

If anything **required** is missing, set `materials_complete: false` and fill `followup` with `doc_type: "vendor-materials-request"`, `audience: "vendor"`. Each question is one missing item: what is needed, why, expected answer type (`evidence attachment` or `link to trust portal`).
