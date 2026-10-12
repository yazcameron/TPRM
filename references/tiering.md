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

## Zip dropdown selections

The 12-row vendor risk tiering table is a proposed reading. It is not a scored Zip tier. Mark the proposed tier Unconfirmed until the reviewer scores Zip.

Each **Selection** must be copied exactly from the list for that question. The Vendor Tiering sheet uses Low, Medium, and High as score columns. Those words are the Zip dropdown only where this list says so. On every other question, a score word is the wrong label.

Source: [Vendor Tiering](https://docs.google.com/spreadsheets/d/1R_nHZmyaVyYz7NGWXBQ5c-ApJeAHKry52R3oBnA5jTI), updated 29 Sep 2026. Zip labels below were confirmed against the form.

### 1. How is Personal Information (PI) handled by this vendor/system?

- `Plain PI (no scrubbing)`
- `PI Anonymized`
- `PI Removed/ Truly Anonymized`

Hashed, tokenized, or masked identifiers are `PI Anonymized`, including incidental PI such as an employee login. Raw name, email, address, or other untransformed personal data is `Plain PI (no scrubbing)`.

### 2. What type of data does the vendor/system handle?

- `Low`
- `Medium`
- `High`

`High` is sensitive personal data, including device and IP identifiers. Payment, health, and biometric data are also `High`.

### 3. What is the approximate volume of data?

- `Low`
- `Medium`
- `High`

`High` is more than 1 million records or an enterprise-wide population, including all activated users.

### 4. How critical is the vendor/system to daily operations?

- `Low`
- `Medium`
- `High`

`Medium` is a disruption that slows the work and has a workaround. `High` is an outage that stops core operations.

### 5. Is redundancy or backup available?

- `Strong Redundancy`
- `Limited Redundancy`
- `No Redundancy`

`Medium` is not an option. One cloud provider with regional copies and vendor-stated backups is `Limited Redundancy`. Multiple providers is `Strong Redundancy`. A single point of failure is `No Redundancy`.

### 6. Would downtime or breach cause measurable revenue impact?

- `Low`
- `Medium`
- `High`

`Medium` is an indirect impact. `High` is a direct hit to payments, Marketplace, Storefront Pro, or Carrot Ads.

### 7. What level of access does the vendor/system have?

- `No system/data access`
- `Read-only access`
- `Privileged access`

`Medium` is not an option. A file-drop or other partial login that is not an admin role or an API token is `Read-only access`. Admin rights, API tokens, and other privileged non-human identities are `Privileged access`.

### 8. Does the vendor connect into critical systems/networks?

- `No integration`
- `Direct integration with corporate apps`
- `Direct integration with core apps`

`Medium` is not an option. A production path into Instacart systems, including dataeng SFTP, a CDP, or an API, is `Direct integration with core apps`. Corporate systems such as a legal or SOP tool are `Direct integration with corporate apps`.

### 9. If compromised, would this vendor/system cause public/customer harm?

- `No visible customer impact`
- `Indirect customer impact (delays, inconvenience)`
- `Direct privacy impact to named individuals`

`High` is not an option. `Direct customer impact` is not an option. Exposure of customer identifiers, including hashed device IDs and IP addresses, is `Direct privacy impact to named individuals`. A delay or inconvenience without that exposure is `Indirect customer impact (delays, inconvenience)`.

### 10. Who manages and controls the data?

- `Internal team controlled`
- `Shared responsibility`
- `Third-party controlled`

`Third-party controlled` means the vendor hosts the data and Instacart does not manage the vendor's encryption keys, access approvals, or staff access. `Shared responsibility` means Instacart manages those controls.

### 11. How does the vendor/system handle data storage?

- `No data storage/processing by third party`
- `Data processed only, not stored`
- `Data stored by third party`

Do not prefix these with High, Medium, or Low.

### 12. What level of security/compliance maturity does the vendor have?

- `Low maturity`
- `Moderate maturity`
- `High maturity`

A current ISO 27001 certificate or SOC 2 Type II is `High maturity`. `Moderate maturity` is some policy or certification that is not independently validated. Open test findings stay in the justification. They do not change a current ISO 27001 certificate to `Moderate maturity`.

## Rejected labels

Do not use these. They are not Zip dropdown values:

- Hashed customer identifiers, plus plain employee contact
- Vendor-stated redundancy
- Medium Criticality
- Medium Revenue Impact
- Limited — production SFTP account
- Production file drop, plus a CDP still onboarding
- Outbound file transfer only
- No direct integration declared
- Direct customer impact
- Limited assurance
- Moderate Maturity
- High — Data stored by third party
- Medium on questions 5, 7, or 8
- High on question 9
