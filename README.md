# tprm-reviewer

Vendor security review from intake through a local HTML Risk Assessment Report. Specialists are prompt files in `agents/`; the orchestrator (`SKILL.md`) owns pauses.

**Cursor:** `.cursor/skills/tprm-reviewer/` wraps this skill.  
**Claude Code:** `/grc` routes TPRM / vendor intake / vendor security review here.

Team output: [TPRM Drive folder](https://drive.google.com/drive/folders/1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY) as `{Vendor} / #{Zip}` (e.g. `Salesforce / #4341`). Local working files: `reviews/tprm/<vendor-slug>/` (gitignored).

```bash
python skills/tprm-reviewer/scripts/engagement.py init --vendor "Salesforce" --zip 4341 --repo-root .
python skills/tprm-reviewer/scripts/render_html.py followup --engagement reviews/tprm/acme --payload questions.json
python skills/tprm-reviewer/scripts/render_html.py report --engagement reviews/tprm/acme --payload report.json
```

Tests: `pytest skills/tprm-reviewer/scripts/tests/`
