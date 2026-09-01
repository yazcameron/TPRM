# Risk Assessment Report outline

Save as `risk-assessment-[vendor-name].html` in the engagement folder, then publish to Drive (`{Vendor} / #{Zip}`).

Chat line (verbatim), substituting the vendor name:

`risk-assessment-[vendor-name].html → ready for approval review`

Agents write JSON; `scripts/render_html.py report` renders it.

## Payload

```json
{
  "vendor_name": "Acme",
  "vendor_slug": "acme",
  "tier": "1",
  "engagement_summary": "Plain-language: what they do, why onboarded, who requested.",
  "data_profile": {
    "personal_information": "Types and categories, or none.",
    "data_sharing_mechanism": "API, file transfer, direct access, etc.",
    "integration_type_and_depth": "What is connected and how deep."
  },
  "scope": {
    "products_and_services": ["Product A"],
    "ai_features": false,
    "ai_features_description": "",
    "data_flow": "Describe or mermaid-as-text. Keep short."
  },
  "baseline_snapshot": {
    "vendor_posture": {
      "security_reports": [
        {"type": "SOC 2 Type 2", "period_or_date": "", "status": "present", "notes": ""}
      ],
      "certifications_and_evidence": [
        {"name": "HITRUST", "status": "missing", "notes": ""}
      ],
      "regulatory_compliance": [
        {"name": "GDPR", "status": "confirmed", "notes": ""}
      ],
      "sfp_eu_30_day_notice": {
        "required": true,
        "confidence": "required",
        "rationale": "",
        "actions": [
          "30-day notification before go-live",
          "Add as SFP EU subprocessor"
        ]
      },
      "subprocessor_designation": {
        "applicable": true,
        "status": "proposed",
        "notes": ""
      },
      "dpa_msa": {
        "dpa_required": true,
        "dpa_executed": false,
        "msa_executed": true,
        "data_handling_terms_adequate": "unknown",
        "notes": ""
      }
    },
    "implementation_posture": {
      "integration_design": {
        "status": "drafted_unconfirmed",
        "diagram": "",
        "connection_types": ["API"],
        "notes": "Drafted from Glean; unconfirmed by requester."
      },
      "data_access": {"fields_tables_datasets": [], "notes": ""},
      "service_accounts": [
        {"name": "", "access": "read-only", "environment": "prod", "scope": "", "notes": ""}
      ],
      "app_owner_signoffs": [
        {"system": "Salesforce", "owner": "", "signed_off": false, "notes": ""}
      ]
    }
  },
  "risks": [
    {
      "title": "Short finding name",
      "mapped_to": "control gap | SOC 2 exception | unresolved follow-up",
      "detail": "What we found.",
      "level": "High",
      "mitigation": "Condition or recommended control."
    }
  ]
}
```

`level` is `High`, `Medium`, or `Low`.

Section 4 is Baseline Snapshot (`baseline_snapshot`). Rules: `references/baseline-snapshot.md`.

- `sfp_eu_30_day_notice.confidence` is `required`, `possible`, or `not_required`.
- `integration_design.status` is `not_required`, `requester_provided`, `drafted_unconfirmed`, or `missing`.
- List `status` values: `present`, `missing`, `not_applicable`, `confirmed`, `unconfirmed`.
- Never omit `baseline_snapshot`; use Unknown / Unconfirmed / N/A rather than dropping fields.

Do not compile the report while any follow-up is unresolved (`paused_on` set, or specialist JSON still has `needs_followup: true`).
