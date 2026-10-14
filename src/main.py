from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from src.config import OUTPUT_PATH
from src.pdf.font_loader import register_fonts
from src.pdf.helpers import register_paragraph_fonts
from src.pdf.pdf_generator import generate_pdf
from src.publication import build_publication_metadata


# ============================================================
# ONEPAGE STUDY - EDITORIALS DAILY
# MAIN
# ============================================================


# ============================================================
# OPTIONS
# ============================================================

# True:
# Open the generated PDF automatically after creation.
#
# False:
# Generate the PDF without opening it.

OPEN_PDF = False


# ============================================================
# OPEN PDF
# ============================================================

def _open_pdf(
    pdf_path: Path,
) -> None:
    """
    Open the generated PDF using the operating system's
    default PDF viewer.
    """

    if not OPEN_PDF:
        return

    if os.name == "nt":
        os.startfile(
            str(pdf_path)
        )
        return

    print(
        "Automatic PDF opening is currently configured "
        "for Windows only."
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Generate the daily OnePage Study editorial PDF.

    Repository creation and output organisation are handled
    separately by repository_manager.
    """

    # --------------------------------------------------------
    # REGISTER PDF FONTS
    # --------------------------------------------------------

    register_fonts()

    # Required for <b> and italic formatting inside
    # ReportLab Paragraph objects.
    register_paragraph_fonts()

    # --------------------------------------------------------
    # PUBLICATION METADATA
    # --------------------------------------------------------

    metadata = (
        build_publication_metadata()
    )

    # --------------------------------------------------------
    # OUTPUT FOLDER
    # --------------------------------------------------------

    publication_date = metadata.publication_date
    if isinstance(publication_date, datetime):
        edition_date = publication_date.date()
    elif isinstance(publication_date, date):
        edition_date = publication_date
    else:
        edition_date = datetime.strptime(
            str(publication_date).strip(), "%d %B %Y"
        ).date()

    dated_output_folder = (
        OUTPUT_PATH
        / str(edition_date.year)
        / edition_date.strftime("%m_%B")
    )
    dated_output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # OUTPUT FILE
    # --------------------------------------------------------

    output_path = (
        dated_output_folder
        / metadata.pdf_filename
    )

    # --------------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------------

    generated_pdf = generate_pdf(
        output_path=output_path,
        metadata=metadata,
    )

    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    print()
    print(
        "ONEPAGE STUDY - EDITORIALS DAILY"
    )
    print(
        "--------------------------------"
    )

    print(
        f"Date: {metadata.publication_date}"
    )

    print(
        f"Edition: {metadata.edition_code}"
    )

    print(
        f"PDF: {generated_pdf.name}"
    )

    print()
    print(
        f"Saved to: {generated_pdf}"
    )

    # --------------------------------------------------------
    # OPEN PDF
    # --------------------------------------------------------

    _open_pdf(
        generated_pdf
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()