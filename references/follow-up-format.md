# Follow-up HTML format

Agents do not write HTML. They write a JSON payload; `scripts/render_html.py followup` renders it.

## Payload

```json
{
  "doc_type": "vendor-clarification",
  "title": "Vendor clarification — Acme",
  "vendor_name": "Acme",
  "audience": "requester",
  "intro": "One or two sentences. Why this is needed.",
  "questions": [
    {
      "number": 1,
      "section": "Product in scope",
      "question": "Which Acme product is being onboarded?",
      "expected_answer_type": "short text"
    }
  ]
}
```

`doc_type` must be one of: `vendor-clarification`, `context-discrepancy`, `vendor-materials-request`, `soc2-followup`, `ai-questionnaire-followup`.

`expected_answer_type` examples: `yes/no`, `short text`, `list of products`, `evidence attachment`, `control owner + date`.

## Tone

Professional, simple, direct. No filler, no apology padding, no marketing language. Numbered questions only.
