"""Google Drive folders for TPRM reviews.

New output:
  https://drive.google.com/drive/folders/1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY
  {Vendor Name}/#{zip_request}/

Prior reviews (read-only source):
  https://drive.google.com/drive/folders/1_PFYmK7yZLiY0fYzKqPU_HA1NF0ml-QN
"""

from __future__ import annotations

import re

DRIVE_ROOT_ID = "1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY"
DRIVE_ROOT_URL = (
    f"https://drive.google.com/drive/folders/{DRIVE_ROOT_ID}"
)

PRIOR_REVIEWS_FOLDER_ID = "1_PFYmK7yZLiY0fYzKqPU_HA1NF0ml-QN"
PRIOR_REVIEWS_FOLDER_URL = (
    f"https://drive.google.com/drive/folders/{PRIOR_REVIEWS_FOLDER_ID}"
)


def format_zip_folder(zip_request: str | int | None) -> str | None:
    """Return '#4341' or None. Accepts '4341', '#4341', 'Zip #4341'."""
    if zip_request is None:
        return None
    digits = re.sub(r"[^0-9]", "", str(zip_request))
    if not digits:
        return None
    return f"#{digits}"


def drive_folder_segments(
    vendor_name: str,
    zip_request: str | int | None = None,
) -> list[str]:
    """Folder names under the TPRM Drive root, vendor first, then Zip # if any."""
    vendor = (vendor_name or "").strip() or "Unknown Vendor"
    parts = [vendor]
    zip_folder = format_zip_folder(zip_request)
    if zip_folder:
        parts.append(zip_folder)
    return parts


def drive_path_display(
    vendor_name: str,
    zip_request: str | int | None = None,
) -> str:
    return " / ".join(drive_folder_segments(vendor_name, zip_request))
