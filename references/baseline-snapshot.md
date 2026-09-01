# Baseline Snapshot

Facts for report section 4. Load during intake, context, and report. Do not omit the section; use Unknown / Unconfirmed / N/A instead of dropping fields.

Schema: `references/report-outline.md`. Persist cross-phase facts on `state.json`: `systems_touched`, `dpa_required`, `dpa_executed`, `eu_personal_data`, `sfp_in_scope`, `subprocessor`, `integration_design_status`.

## DPA required

- **Yes** if the vendor processes or accesses PI/PII, or is a subprocessor (vendor processes personal data on Instacart's behalf).
- **No** typically for Tier 3 / no personal data.
- Independent of whether a DPA is already signed. Record both `dpa_required` and `dpa_executed`.

## SFP EU 30-day notice

SFP = Storefront Pro. Instacart is processor on SFP; a vendor that processes SFP EU personal data is a subprocessor.

**Required** when all of:

1. Vendor processes personal data on Instacart's behalf (subprocessor pattern), and
2. EU/EEA data is in scope **or** the integration touches SFP, and
3. Go-live would add them as a processor/subprocessor for SFP EU

**Possible** when (1) is true but EU/SFP is unknown — never silently mark No.

If required or possible, the report callout must include both actions: send 30-day notification **before go-live**, and add the vendor as a subprocessor for SFP EU.

## Integration design — required or not

Do not treat a design doc as mandatory for every vendor. Use judgement.

**Not required** when there is no systematic information flow between Instacart systems and the vendor. Typical case: employees sign into a vendor portal / SaaS UI (browser login) and work there; no API, file drop, service account, shared drive, SDK, webhook, or warehouse access. Set `integration_design.status` to `not_required` with a one-line rationale (e.g. "Portal login only; no systematic data flow."). Do not draft a diagram. Do not ask the requester for a design doc.

**Required** when any of: API or SDK; file transfer / SFTP / shared drive; service account; webhook pushing Instacart data; production or non-prod access to an Instacart system (Salesforce, Workday, Okta, Snowflake, …); vendor pulling or receiving datasets.

**Uncertain:** prefer required and draft Unconfirmed (safer).

SSO/Okta used only so humans can log into the vendor portal does **not** by itself make a full integration design required. Mention Okta in notes if relevant; do not invent a data-flow diagram.

If required and the requester provided a design: `requester_provided`. If required and they did not: draft mermaid from Glean + intake, status `drafted_unconfirmed`, labeled Unconfirmed in the HTML. If required but there is not enough context to draft: `missing`.

Do not open `vendor-clarification` solely to request a design for a portal-only tool. If clarification is already happening **and** a design is required, add a question to confirm the draft.

## App owner sign-off

One row per named Instacart system actually touched by a technical integration. Skip systems that are not connected. A SaaS portal with no IdP/API/export does not need a sign-off table.

## Report findings

If SFP EU 30-day notice is required/possible, or DPA is required but not executed, also add a Risk Summary finding so the flag is not only in the snapshot.
