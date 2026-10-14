from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path


# ============================================================
# ONEPAGE STUDY - EDITORIALS DAILY
# OUTPUT MANAGER
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

# This file is located at:
#
# project_root/
#   repository/
#     manager/
#       output_manager.py
#
# Therefore we go up three levels to reach project root.

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_JSON = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output"
)


# ============================================================
# OPTIONS
# ============================================================

# Open the final organised PDF automatically after moving it.

OPEN_PDF = True


# ============================================================
# LOAD INPUT
# ============================================================

def load_input() -> dict:
    """
    Load the validated INPUT.json file.
    """

    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            f"INPUT.json was not found:\n{INPUT_JSON}"
        )

    with INPUT_JSON.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# BUILD MONTH FOLDER
# ============================================================

def build_month_folder(
    publication_date: datetime,
) -> Path:
    """
    Create and return:

        output/
            YYYY/
                MM_Month/
    """

    year_folder = str(
        publication_date.year
    )

    month_folder = (
        f"{publication_date.month:02d}_"
        f"{publication_date.strftime('%B')}"
    )

    destination = (
        OUTPUT_ROOT
        / year_folder
        / month_folder
    )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    return destination


# ============================================================
# ORGANISE DAILY PDF
# ============================================================

def organise_daily_pdf() -> Path:
    """
    Move the newly generated daily PDF from:

        output/
            UAK_Editorials_Daily_YYMMDD.pdf

    into:

        output/
            YYYY/
                MM_Month/
                    UAK_Editorials_Daily_YYMMDD.pdf

    If the same date is generated again, replace the
    previously organised version.
    """

    data = load_input()

    publication_date_text = data[
        "publication_date"
    ]

    publication_date = datetime.strptime(
        publication_date_text,
        "%d %B %Y",
    )

    date_code = publication_date.strftime(
        "%y%m%d"
    )

    filename = (
        f"UAK_Editorials_Daily_{date_code}.pdf"
    )

    # --------------------------------------------------------
    # SOURCE PDF
    # --------------------------------------------------------

    source_pdf = (
        OUTPUT_ROOT
        / filename
    )

    if not source_pdf.exists():
        raise FileNotFoundError(
            "Generated daily PDF was not found:\n"
            f"{source_pdf}"
        )

    # --------------------------------------------------------
    # DESTINATION
    # --------------------------------------------------------

    destination_folder = (
        build_month_folder(
            publication_date
        )
    )

    destination_pdf = (
        destination_folder
        / filename
    )

    # --------------------------------------------------------
    # SAME-DATE REGENERATION
    # --------------------------------------------------------

    if destination_pdf.exists():
        destination_pdf.unlink()

    # --------------------------------------------------------
    # MOVE PDF
    # --------------------------------------------------------

    shutil.move(
        str(source_pdf),
        str(destination_pdf),
    )

    return destination_pdf


# ============================================================
# OPEN FINAL PDF
# ============================================================

def open_pdf(
    pdf_path: Path,
) -> None:
    """
    Open the PDF only after it has reached its
    final Year/Month location.
    """

    if not OPEN_PDF:
        return

    if not pdf_path.exists():
        raise FileNotFoundError(
            "Final PDF was not found:\n"
            f"{pdf_path}"
        )

    if os.name == "nt":
        os.startfile(
            str(pdf_path)
        )
        return

    print(
        "Automatic PDF opening is currently "
        "configured for Windows only."
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    print()
    print("=" * 72)
    print("ORGANISING DAILY OUTPUT")
    print("=" * 72)

    destination_pdf = (
        organise_daily_pdf()
    )

    print()
    print(
        f"Daily PDF: {destination_pdf}"
    )

    print()
    print("=" * 72)
    print("DAILY OUTPUT ORGANISED")
    print("=" * 72)

    # Open only after the PDF has been moved
    # to its permanent location.

    open_pdf(
        destination_pdf
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )