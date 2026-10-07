from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

from src.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PUBLICATION_SUBTITLE,
    PUBLICATION_TITLE,
)


# ============================================================
# ONEPAGE STUDY • EDITORIALS DAILY
# PUBLICATION METADATA
# ============================================================


# ============================================================
# PRODUCT IDENTITY
# ============================================================

# Master brand:
# UPSC Anchor with Kumar
#
# Product:
# ONEPAGE STUDY • EDITORIALS DAILY
#
# Edition example:
# UAK-ED-261007
#
# PDF example:
# UAK_Editorials_Daily_261007.pdf

EDITION_PREFIX: Final[str] = "UAK-ED"

PDF_FILENAME_PREFIX: Final[str] = (
    "UAK_Editorials_Daily"
)


# ============================================================
# PUBLIC CHANNELS
# ============================================================

TELEGRAM_HANDLE: Final[str] = (
    "@upscanchorwithkumar"
)

# Keep empty until the final website/domain is confirmed.
WEBSITE: Final[str] = ""


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parent.parent
)

INPUT_JSON_PATH: Final[Path] = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)


# ============================================================
# DATE FORMAT
# ============================================================

PUBLICATION_DATE_FORMAT: Final[str] = (
    "%d %B %Y"
)


# ============================================================
# PUBLICATION METADATA
# ============================================================

@dataclass(frozen=True, slots=True)
class PublicationMetadata:
    project_name: str
    project_version: str

    title: str
    subtitle: str
    footer_brand: str

    publication_date: str
    publication_date_iso: str

    edition_code: str
    pdf_filename: str

    telegram_handle: str
    website: str


# ============================================================
# INPUT METADATA LOADER
# ============================================================

def _load_input_metadata() -> tuple[str, str]:
    """
    Load and validate the publication date from INPUT.json.

    Expected examples:

        publication_date:
            07 October 2026

        publication_date_iso:
            2026-10-07
    """

    try:
        data = json.loads(
            INPUT_JSON_PATH.read_text(
                encoding="utf-8-sig"
            )
        )

    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "INPUT.json was not found.\n"
            "Run the text-to-JSON converter first:\n"
            f"{INPUT_JSON_PATH}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ValueError(
            "INPUT.json contains invalid JSON at "
            f"line {exc.lineno}, "
            f"column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    except OSError as exc:
        raise OSError(
            "Unable to read INPUT.json: "
            f"{exc}"
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "INPUT.json root must be a JSON object."
        )

    publication_date = str(
        data.get(
            "publication_date",
            "",
        )
    ).strip()

    publication_date_iso = str(
        data.get(
            "publication_date_iso",
            "",
        )
    ).strip()

    if not publication_date:
        raise ValueError(
            "INPUT.json is missing "
            "'publication_date'."
        )

    if not publication_date_iso:
        raise ValueError(
            "INPUT.json is missing "
            "'publication_date_iso'."
        )

    # --------------------------------------------------------
    # VALIDATE DISPLAY DATE
    # --------------------------------------------------------

    try:
        parsed_display_date = datetime.strptime(
            publication_date,
            PUBLICATION_DATE_FORMAT,
        )

    except ValueError as exc:
        raise ValueError(
            "INPUT.json publication_date must use "
            "the format 'DD Month YYYY', for example "
            "'07 October 2026'."
        ) from exc

    # --------------------------------------------------------
    # VALIDATE ISO DATE
    # --------------------------------------------------------

    try:
        parsed_iso_date = datetime.strptime(
            publication_date_iso,
            "%Y-%m-%d",
        )

    except ValueError as exc:
        raise ValueError(
            "INPUT.json publication_date_iso must use "
            "the format 'YYYY-MM-DD'."
        ) from exc

    # --------------------------------------------------------
    # BOTH DATES MUST REPRESENT THE SAME DAY
    # --------------------------------------------------------

    if (
        parsed_display_date.date()
        != parsed_iso_date.date()
    ):
        raise ValueError(
            "publication_date and "
            "publication_date_iso represent "
            "different dates."
        )

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    normalized_display_date = (
        parsed_display_date.strftime(
            PUBLICATION_DATE_FORMAT
        )
    )

    normalized_iso_date = (
        parsed_iso_date.strftime(
            "%Y-%m-%d"
        )
    )

    return (
        normalized_display_date,
        normalized_iso_date,
    )


# ============================================================
# EDITION CODE
# ============================================================

def build_edition_code(
    publication_date_iso: str,
) -> str:
    """
    Build the Editorials Daily edition code.

    Example:

        2026-10-07
        ↓
        UAK-ED-261007
    """

    parsed_date = datetime.strptime(
        publication_date_iso,
        "%Y-%m-%d",
    )

    date_code = parsed_date.strftime(
        "%y%m%d"
    )

    return (
        f"{EDITION_PREFIX}-"
        f"{date_code}"
    )


# ============================================================
# PDF FILENAME
# ============================================================

def build_pdf_filename(
    publication_date_iso: str,
) -> str:
    """
    Build the Editorials Daily PDF filename.

    Example:

        2026-10-07
        ↓
        UAK_Editorials_Daily_261007.pdf
    """

    parsed_date = datetime.strptime(
        publication_date_iso,
        "%Y-%m-%d",
    )

    date_code = parsed_date.strftime(
        "%y%m%d"
    )

    return (
        f"{PDF_FILENAME_PREFIX}_"
        f"{date_code}.pdf"
    )


# ============================================================
# METADATA FACTORY
# ============================================================

def build_publication_metadata() -> PublicationMetadata:
    """
    Create the shared publication metadata for
    OnePage Study • Editorials Daily.

    The publication date entered in INPUT.json controls:

    - the date shown in the PDF header;
    - the UAK-ED edition code;
    - the generated PDF filename.
    """

    (
        publication_date,
        publication_date_iso,
    ) = _load_input_metadata()

    edition_code = build_edition_code(
        publication_date_iso
    )

    pdf_filename = build_pdf_filename(
        publication_date_iso
    )

    return PublicationMetadata(
        project_name=PROJECT_NAME,
        project_version=PROJECT_VERSION,

        title=PUBLICATION_TITLE,
        subtitle=PUBLICATION_SUBTITLE,

        # Master brand remains UPSC Anchor with Kumar.
        footer_brand=PUBLICATION_SUBTITLE,

        publication_date=publication_date,
        publication_date_iso=(
            publication_date_iso
        ),

        edition_code=edition_code,
        pdf_filename=pdf_filename,

        telegram_handle=TELEGRAM_HANDLE,
        website=WEBSITE,
    )