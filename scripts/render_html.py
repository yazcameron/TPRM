"""Render TPRM follow-up and report HTML from JSON payloads."""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "templates"

FOLLOWUP_FILES = {
    "vendor-clarification": "vendor-clarification.html",
    "context-discrepancy": "context-discrepancy.html",
    "vendor-materials-request": "vendor-materials-request.html",
    "soc2-followup": "soc2-followup.html",
    "ai-questionnaire-followup": "ai-questionnaire-followup.html",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fill(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def wrap(title: str, body: str) -> str:
    base = (TEMPLATES / "base.html").read_text(encoding="utf-8")
    return fill(base, {"title": html.escape(title), "body": body, "generated": utc_now()})


def render_questions(questions: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for q in questions:
        number = q.get("number", len(parts) + 1)
        section = html.escape(str(q.get("section", "")))
        question = html.escape(str(q.get("question", "")))
        expected = html.escape(str(q.get("expected_answer_type", "")))
        parts.append(
            f'<li value="{html.escape(str(number))}">'
            f'<div class="section">{section}</div>'
            f'<p class="q">{question}</p>'
            f'<div class="expect">Expected: {expected}</div>'
            f"</li>"
        )
    return "\n".join(parts)


def render_followup(payload: dict[str, Any]) -> tuple[str, str]:
    doc_type = payload.get("doc_type")
    if doc_type not in FOLLOWUP_FILES:
        raise ValueError(f"Unknown doc_type: {doc_type}")
    filename = FOLLOWUP_FILES[doc_type]
    questions = payload.get("questions") or []
    if not questions:
        raise ValueError("follow-up requires at least one question")
    inner = (TEMPLATES / "followup.html").read_text(encoding="utf-8")
    title = str(payload.get("title") or filename)
    body = fill(
        inner,
        {
            "title": html.escape(title),
            "vendor_name": html.escape(str(payload.get("vendor_name", ""))),
            "audience": html.escape(str(payload.get("audience", ""))),
            "intro": html.escape(str(payload.get("intro", ""))),
            "questions": render_questions(questions),
        },
    )
    return filename, wrap(title, body)


def _dl(items: list[tuple[str, str]]) -> str:
    parts = ["<dl>"]
    for dt, dd in items:
        parts.append(f"<dt>{html.escape(dt)}</dt><dd>{html.escape(dd)}</dd>")
    parts.append("</dl>")
    return "\n".join(parts)


def _status_list(rows: list[dict[str, Any]], name_key: str = "name") -> str:
    if not rows:
        return "None recorded."
    bits: list[str] = []
    for row in rows:
        label = str(row.get(name_key) or row.get("type") or "Item")
        status = str(row.get("status") or "unconfirmed")
        notes = str(row.get("notes") or "").strip()
        period = str(row.get("period_or_date") or "").strip()
        extra = "; ".join(p for p in (period, notes) if p)
        bits.append(f"{label}: {status}" + (f" ({extra})" if extra else ""))
    return "; ".join(bits)


def _baseline_snapshot_html(snapshot: dict[str, Any] | None) -> str:
    if not snapshot:
        return "<p>Unknown / Unconfirmed / N/A</p>"
    vendor = snapshot.get("vendor_posture") or {}
    impl = snapshot.get("implementation_posture") or {}
    sfp = vendor.get("sfp_eu_30_day_notice") or {}
    sub = vendor.get("subprocessor_designation") or {}
    dpa = vendor.get("dpa_msa") or {}
    integ = impl.get("integration_design") or {}
    access = impl.get("data_access") or {}
    sfp_conf = str(sfp.get("confidence") or "unconfirmed")
    sfp_req = "Yes" if sfp.get("required") else "No"
    sfp_actions = sfp.get("actions") or []
    if isinstance(sfp_actions, list):
        sfp_action_text = "; ".join(str(a) for a in sfp_actions) if sfp_actions else "N/A"
    else:
        sfp_action_text = str(sfp_actions)
    svc_accounts = impl.get("service_accounts") or []
    if svc_accounts:
        svc_text = "; ".join(
            str(a.get("name") or "unnamed") + (f" ({a.get('access', '')}" if a.get("access") else "")
            for a in svc_accounts
        )
    else:
        svc_text = "None"
    signoffs = impl.get("app_owner_signoffs") or []
    if signoffs:
        sign_text = "; ".join(
            f"{s.get('system', 'system')}: {'signed' if s.get('signed_off') else 'not signed'}"
            for s in signoffs
        )
    else:
        sign_text = "N/A (no Instacart systems connected)"
    conn = integ.get("connection_types") or []
    conn_text = ", ".join(str(c) for c in conn) if isinstance(conn, list) and conn else "None"
    fields = access.get("fields_tables_datasets") or []
    fields_text = ", ".join(str(f) for f in fields) if isinstance(fields, list) and fields else "Unknown"
    blocks = [
        "<h3>Vendor posture</h3>",
        _dl(
            [
                ("Security reports", _status_list(vendor.get("security_reports") or [], "type")),
                (
                    "Certifications and evidence",
                    _status_list(vendor.get("certifications_and_evidence") or []),
                ),
                (
                    "Regulatory compliance",
                    _status_list(vendor.get("regulatory_compliance") or []),
                ),
                (
                    "SFP EU 30-day notice",
                    f"{sfp_req} ({sfp_conf}). {sfp.get('rationale') or 'Unconfirmed.'} Actions: {sfp_action_text}",
                ),
                (
                    "Subprocessor designation",
                    f"Applicable: {sub.get('applicable', 'unknown')}; status: {sub.get('status') or 'unconfirmed'}. {sub.get('notes') or ''}".strip(),
                ),
                (
                    "DPA / MSA",
                    (
                        f"DPA required: {dpa.get('dpa_required')}; executed: {dpa.get('dpa_executed')}. "
                        f"MSA executed: {dpa.get('msa_executed')}. "
                        f"Data-handling terms: {dpa.get('data_handling_terms_adequate') or 'unknown'}. "
                        f"{dpa.get('notes') or ''}"
                    ).strip(),
                ),
            ]
        ),
        "<h3>Implementation posture</h3>",
        _dl(
            [
                (
                    "Integration design",
                    f"{integ.get('status') or 'unknown'}. {integ.get('notes') or ''}".strip(),
                ),
                ("Connection types", conn_text),
                ("Data access", f"{fields_text}. {access.get('notes') or ''}".strip()),
                ("Service accounts", svc_text),
                ("App-owner sign-off", sign_text),
            ]
        ),
    ]
    diagram = str(integ.get("diagram") or "").strip()
    if diagram:
        blocks.append("<pre>" + html.escape(diagram) + "</pre>")
    return "\n".join(blocks)


def _follow_ups_html(follow_ups: dict[str, Any] | list[dict[str, Any]] | None) -> tuple[str, str]:
    """Return (intro, body HTML). Empty payload yields a one-line N/A section."""
    if not follow_ups:
        return "No open scoping or review follow-ups.", "<p>None.</p>"
    if isinstance(follow_ups, list):
        intro, items = "", follow_ups
    else:
        intro = str(follow_ups.get("intro") or "")
        items = follow_ups.get("items") or follow_ups.get("questions") or []
    if not items:
        return intro or "No open scoping or review follow-ups.", "<p>None.</p>"
    rows: list[str] = []
    for item in items:
        number = html.escape(str(item.get("number") or ""))
        section = html.escape(str(item.get("section") or ""))
        question = html.escape(str(item.get("question") or ""))
        status = html.escape(str(item.get("status") or "open"))
        audience = html.escape(str(item.get("audience") or ""))
        current = html.escape(str(item.get("current_answer") or "—"))
        needed = html.escape(str(item.get("needed") or item.get("expected_answer_type") or "—"))
        rows.append(
            "<tr>"
            f"<td>{number}</td>"
            f"<td>{section}</td>"
            f"<td>{question}</td>"
            f"<td>{status}</td>"
            f"<td>{audience}</td>"
            f"<td>{current}</td>"
            f"<td>{needed}</td>"
            "</tr>"
        )
    table = (
        "<table><thead><tr>"
        "<th>#</th><th>Section</th><th>Question</th><th>Status</th>"
        "<th>Audience</th><th>Current answer</th><th>Still needed</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
    return intro, table


def _risks_table(risks: list[dict[str, Any]]) -> str:
    if not risks:
        return "<p>No findings recorded.</p>"
    rows: list[str] = []
    for r in risks:
        level = html.escape(str(r.get("level", "")))
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(r.get('title', '')))}</td>"
            f"<td>{html.escape(str(r.get('mapped_to', '')))}</td>"
            f"<td>{html.escape(str(r.get('detail', '')))}</td>"
            f'<td class="level-{level}">{level}</td>'
            f"<td>{html.escape(str(r.get('mitigation', '')))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Finding</th><th>Mapped to</th><th>Detail</th><th>Level</th><th>Mitigation</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def render_report(payload: dict[str, Any]) -> tuple[str, str]:
    vendor_name = str(payload.get("vendor_name") or "vendor")
    slug = str(payload.get("vendor_slug") or _slug(vendor_name))
    filename = f"risk-assessment-{slug}.html"
    data = payload.get("data_profile") or {}
    scope = payload.get("scope") or {}
    products = scope.get("products_and_services") or []
    if isinstance(products, list):
        products_text = ", ".join(str(p) for p in products) if products else "—"
    else:
        products_text = str(products)
    ai = bool(scope.get("ai_features"))
    ai_desc = str(scope.get("ai_features_description") or "")
    if ai:
        ai_block = "Yes. " + ai_desc if ai_desc else "Yes."
    else:
        ai_block = "No."
    follow_intro, follow_body = _follow_ups_html(payload.get("follow_ups"))
    inner = (TEMPLATES / "report.html").read_text(encoding="utf-8")
    title = f"Risk Assessment Report — {vendor_name}"
    body = fill(
        inner,
        {
            "vendor_name": html.escape(vendor_name),
            "tier": html.escape(str(payload.get("tier", ""))),
            "engagement_summary": html.escape(str(payload.get("engagement_summary", ""))),
            "personal_information": html.escape(str(data.get("personal_information", ""))),
            "data_sharing_mechanism": html.escape(str(data.get("data_sharing_mechanism", ""))),
            "integration_type_and_depth": html.escape(
                str(data.get("integration_type_and_depth", ""))
            ),
            "deletion_posture": html.escape(
                str(data.get("deletion_posture") or "Unknown / not described in the VSQ.")
            ),
            "products_and_services": html.escape(products_text),
            "ai_features_block": html.escape(ai_block),
            "data_flow": html.escape(str(scope.get("data_flow", ""))),
            "baseline_snapshot": _baseline_snapshot_html(payload.get("baseline_snapshot")),
            "risks_table": _risks_table(payload.get("risks") or []),
            "follow_ups_intro": html.escape(follow_intro),
            "follow_ups_block": follow_body,
        },
    )
    return filename, wrap(title, body)


def _slug(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "vendor"


def write_html(engagement: Path, filename: str, content: str) -> Path:
    engagement.mkdir(parents=True, exist_ok=True)
    path = engagement / filename
    path.write_text(content, encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render TPRM HTML from JSON")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_f = sub.add_parser("followup")
    p_f.add_argument("--engagement", type=Path, required=True)
    p_f.add_argument("--payload", type=Path, required=True)

    p_r = sub.add_parser("report")
    p_r.add_argument("--engagement", type=Path, required=True)
    p_r.add_argument("--payload", type=Path, required=True)

    args = parser.parse_args(argv)
    try:
        payload = load_json(args.payload)
        if args.cmd == "followup":
            filename, html_doc = render_followup(payload)
        else:
            filename, html_doc = render_report(payload)
        path = write_html(args.engagement, filename, html_doc)
        print(path)
        return 0
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
