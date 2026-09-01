# Vendor tiering

Assign one tier from intake data sensitivity and integration depth. Record it on `state.json` as `"1"`, `"2"`, or `"3"`.

## Tier 1 — high sensitivity, deep integration

Use when any of these are true:

- Sub-processor or similar (vendor processes personal data on Instacart's behalf)
- Access to PII, payment data, account credentials, or other high-sensitivity data
- Production access, deep API integration, or embedded SDK in a customer-facing or core ops path
- AI features that train on, log, or otherwise persist Instacart or customer data

Required materials: SOC 2 report, AI questionnaire (if AI is in scope), VSQ, security docs.

## Tier 2 — moderate sensitivity or limited integration

Use when:

- Some business or limited personal data, but not a sub-processor pattern
- SSO, webhook, or scoped API without broad data access
- Internal tool with limited data fields

Required materials: trust portal or VSQ; SOC 2 if available.

## Tier 3 — low sensitivity, no personal data

Use when:

- No personal data
- Shallow or no technical integration (content, marketing, publicly available data)

Required materials: trust portal or basic security docs.

## Tie-breakers

- If PII is in scope, do not assign Tier 3.
- If both a deep integration and PII exist, assign Tier 1.
- Prefer the higher tier when evidence is mixed. Note the reason in `state.json` `notes`.
