"""TPRM engagement workspace: create, pause, confirm, load state."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from drive_output import drive_path_display, format_zip_folder


PHASES = (
    "start",
    "intake",
    "context",
    "controls",
    "review",
    "report",
    "complete",
)

DOC_TYPES = (
    "vendor-clarification.html",
    "context-discrepancy.html",
    "vendor-materials-request.html",
    "soc2-followup.html",
    "ai-questionnaire-followup.html",
)

AUDIENCES = ("requester", "vendor")


class EngagementError(RuntimeError):
    """Invalid engagement transition."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "vendor"


def default_state(vendor_name: str, vendor_slug: str, zip_request: str | None = None) -> dict[str, Any]:
    zip_folder = format_zip_folder(zip_request)
    return {
        "vendor_name": vendor_name,
        "vendor_slug": vendor_slug,
        "zip_request_number": zip_folder,
        "drive_path": drive_path_display(vendor_name, zip_folder),
        "drive_folder_id": None,
        "drive_doc_urls": {},
        "tier": None,
        "requester": {"name": "", "email": "", "team": ""},
        "description": "",
        "integration_type": "",
        "data_shared": [],
        "products_in_scope": [],
        "ai_features": False,
        "ai_features_description": "",
        "materials": {
            "soc2": False,
            "ai_questionnaire": False,
            "vsq": False,
            "trust_portal": False,
            "security_docs": False,
        },
        "prior_reviews": [],
        "phase": "start",
        "paused_on": None,
        "paused_audience": None,
        "confirmations": {},
        "scope_changed": False,
        "prior_reviews_drive_available": None,
        "glean_available": None,
        "safe_available": None,
        "notes": [],
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }


def repo_reviews_dir(repo_root: Path) -> Path:
    return repo_root / "reviews" / "tprm"


def engagement_dir(repo_root: Path, slug: str) -> Path:
    return repo_reviews_dir(repo_root) / slug


def state_path(eng_dir: Path) -> Path:
    return eng_dir / "state.json"


def load_state(eng_dir: Path) -> dict[str, Any]:
    path = state_path(eng_dir)
    if not path.exists():
        raise EngagementError(f"No state.json at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(eng_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    path = state_path(eng_dir)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def init_engagement(
    repo_root: Path,
    vendor_name: str,
    slug: str | None = None,
    zip_request: str | None = None,
) -> Path:
    vendor_slug = slug or slugify(vendor_name)
    eng = engagement_dir(repo_root, vendor_slug)
    (eng / "inputs").mkdir(parents=True, exist_ok=True)
    path = state_path(eng)
    if path.exists():
        existing = load_state(eng)
        if existing.get("vendor_name") and existing["vendor_name"] != vendor_name:
            raise EngagementError(
                f"Engagement {vendor_slug} already exists for {existing['vendor_name']}"
            )
        if zip_request:
            apply_fields(eng, {"zip_request_number": format_zip_folder(zip_request)})
        return eng
    save_state(eng, default_state(vendor_name, vendor_slug, zip_request))
    return eng


def assert_not_paused(state: dict[str, Any]) -> None:
    paused = state.get("paused_on")
    if paused:
        audience = state.get("paused_audience") or "requester / vendor"
        raise EngagementError(
            f"Paused on {paused}. Confirm with {audience} before moving forward."
        )


def pause(eng_dir: Path, filename: str, audience: str) -> dict[str, Any]:
    if filename not in DOC_TYPES:
        raise EngagementError(f"Unknown follow-up file: {filename}")
    if audience not in AUDIENCES:
        raise EngagementError(f"Audience must be requester or vendor, got {audience}")
    html_path = eng_dir / filename
    if not html_path.exists():
        raise EngagementError(f"Render {filename} before pausing (missing {html_path})")
    state = load_state(eng_dir)
    state["paused_on"] = filename
    state["paused_audience"] = audience
    save_state(eng_dir, state)
    return state


def confirm(eng_dir: Path, filename: str) -> dict[str, Any]:
    state = load_state(eng_dir)
    paused = state.get("paused_on")
    if paused and paused != filename:
        raise EngagementError(f"Paused on {paused}, not {filename}")
    if not paused:
        raise EngagementError("Nothing is paused")
    confirmations = dict(state.get("confirmations") or {})
    confirmations[filename] = utc_now()
    state["confirmations"] = confirmations
    state["paused_on"] = None
    state["paused_audience"] = None
    save_state(eng_dir, state)
    return state


def advance(eng_dir: Path, phase: str) -> dict[str, Any]:
    if phase not in PHASES:
        raise EngagementError(f"Unknown phase: {phase}")
    state = load_state(eng_dir)
    assert_not_paused(state)
    state["phase"] = phase
    save_state(eng_dir, state)
    return state


def complete(eng_dir: Path) -> dict[str, Any]:
    return advance(eng_dir, "complete")


def apply_fields(eng_dir: Path, fields: dict[str, Any]) -> dict[str, Any]:
    state = load_state(eng_dir)
    for key, value in fields.items():
        if key in ("paused_on", "paused_audience"):
            raise EngagementError("Use pause/confirm to change pause fields")
        if key == "zip_request_number":
            value = format_zip_folder(value)
        state[key] = value
    state["drive_path"] = drive_path_display(
        str(state.get("vendor_name") or ""),
        state.get("zip_request_number"),
    )
    save_state(eng_dir, state)
    return state


def _add_repo_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="GRC-tools repo root (default: cwd)",
    )


def _eng_from_args(args: argparse.Namespace) -> Path:
    return engagement_dir(args.repo_root.resolve(), args.slug)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TPRM engagement state")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create engagement folder + state.json")
    p_init.add_argument("--vendor", required=True)
    p_init.add_argument("--slug")
    p_init.add_argument("--zip", dest="zip_request", help="Zip request number, e.g. 4341")
    _add_repo_root(p_init)

    p_drive = sub.add_parser("drive-path", help="Print Drive folder path (Vendor / #Zip)")
    p_drive.add_argument("--vendor", required=True)
    p_drive.add_argument("--zip", dest="zip_request")

    p_status = sub.add_parser("status", help="Print state.json")
    p_status.add_argument("--slug", required=True)
    _add_repo_root(p_status)

    p_pause = sub.add_parser("pause", help="Gate the next phase on a follow-up HTML file")
    p_pause.add_argument("--slug", required=True)
    p_pause.add_argument("--file", required=True)
    p_pause.add_argument("--audience", required=True, choices=AUDIENCES)
    _add_repo_root(p_pause)

    p_confirm = sub.add_parser("confirm", help="Clear pause after human confirmation")
    p_confirm.add_argument("--slug", required=True)
    p_confirm.add_argument("--file", required=True)
    _add_repo_root(p_confirm)

    p_advance = sub.add_parser("advance", help="Set phase (blocked if paused)")
    p_advance.add_argument("--slug", required=True)
    p_advance.add_argument("--phase", required=True, choices=PHASES)
    _add_repo_root(p_advance)

    p_complete = sub.add_parser("complete", help="Mark engagement complete")
    p_complete.add_argument("--slug", required=True)
    _add_repo_root(p_complete)

    p_set = sub.add_parser("set", help="Merge JSON fields into state.json")
    p_set.add_argument("--slug", required=True)
    p_set.add_argument("--json", required=True, help="JSON object string or @path")
    _add_repo_root(p_set)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "init":
            eng = init_engagement(
                args.repo_root.resolve(),
                args.vendor,
                args.slug,
                args.zip_request,
            )
            state = load_state(eng)
            print(eng)
            print(f"Drive: {state.get('drive_path')}")
            return 0
        if args.cmd == "drive-path":
            print(drive_path_display(args.vendor, args.zip_request))
            return 0
        eng = _eng_from_args(args)
        if args.cmd == "status":
            print(json.dumps(load_state(eng), indent=2))
            return 0
        if args.cmd == "pause":
            pause(eng, args.file, args.audience)
            print(f"{args.file} → confirm with {args.audience} before moving forward")
            return 0
        if args.cmd == "confirm":
            confirm(eng, args.file)
            print(f"confirmed {args.file}")
            return 0
        if args.cmd == "advance":
            advance(eng, args.phase)
            print(f"phase={args.phase}")
            return 0
        if args.cmd == "complete":
            complete(eng)
            print("complete")
            return 0
        if args.cmd == "set":
            raw = args.json
            if raw.startswith("@"):
                raw = Path(raw[1:]).read_text(encoding="utf-8")
            fields = json.loads(raw)
            if not isinstance(fields, dict):
                raise EngagementError("--json must be an object")
            apply_fields(eng, fields)
            print("updated")
            return 0
    except EngagementError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
