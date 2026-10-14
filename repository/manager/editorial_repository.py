from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from src.pdf.font_loader import register_fonts
from src.pdf.helpers import (
    make_point_paragraph,
    make_takeaway_paragraph,
)
from src.pdf.theme import (
    FONT_BOLD,
    FONT_REGULAR,
    POINT_TEXT_LEADING,
    POINT_TEXT_SIZE,
    TAKEAWAY_LEADING,
    TAKEAWAY_SIZE,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_JSON = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)

REPOSITORY_ROOT = (
    PROJECT_ROOT
    / "repository"
)


# ============================================================
# PAGE SETTINGS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

LEFT_MARGIN = 18 * mm
RIGHT_MARGIN = 18 * mm
TOP_MARGIN = 18 * mm
BOTTOM_MARGIN = 18 * mm

CONTENT_WIDTH = (
    PAGE_WIDTH
    - LEFT_MARGIN
    - RIGHT_MARGIN
)


# ============================================================
# INPUT
# ============================================================

def load_input() -> dict:
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
# DATE
# ============================================================

def parse_publication_date(
    publication_date: str,
) -> datetime:
    return datetime.strptime(
        publication_date,
        "%d %B %Y",
    )


# ============================================================
# GS FOLDER
# ============================================================

def get_gs_folder(
    gs_paper: str,
) -> str:
    mapping = {
        "GS I": "GS1",
        "GS II": "GS2",
        "GS III": "GS3",
        "GS IV": "GS4",
    }

    normalized = gs_paper.strip().upper()

    if normalized not in mapping:
        raise ValueError(
            f"Unsupported GS paper: {gs_paper}"
        )

    return mapping[normalized]


# ============================================================
# REPOSITORY PATH
# ============================================================

def build_repository_path(
    *,
    publication_date: datetime,
    gs_folder: str,
    editorial_number: int,
) -> Path:

    year_folder = str(
        publication_date.year
    )

    month_folder = (
        f"{publication_date.month:02d}_"
        f"{publication_date.strftime('%B')}"
    )

    date_code = publication_date.strftime(
        "%y%m%d"
    )

    filename = (
        f"UAK_Editorials_Daily_"
        f"{date_code}_"
        f"{editorial_number}.pdf"
    )

    folder = (
        REPOSITORY_ROOT
        / gs_folder
        / year_folder
        / month_folder
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return folder / filename


# ============================================================
# PARAGRAPH DRAWING
# ============================================================

def draw_paragraph(
    paragraph,
    canvas: Canvas,
    *,
    x: float,
    top: float,
    width: float,
) -> float:

    _, height = paragraph.wrap(
        width,
        PAGE_HEIGHT,
    )

    paragraph.drawOn(
        canvas,
        x,
        top - height,
    )

    return top - height


# ============================================================
# SINGLE EDITORIAL PDF
# ============================================================

def generate_editorial_pdf(
    *,
    editorial: dict,
    publication_date_text: str,
    edition_code: str,
    output_path: Path,
) -> Path:

    canvas = Canvas(
        str(output_path),
        pagesize=A4,
    )

    canvas.setTitle(
        editorial["heading"]
    )

    current_y = (
        PAGE_HEIGHT
        - TOP_MARGIN
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    canvas.setFont(
        FONT_BOLD,
        13,
    )

    canvas.drawString(
        LEFT_MARGIN,
        current_y,
        "ONEPAGE STUDY • EDITORIALS DAILY",
    )

    current_y -= 7 * mm

    # --------------------------------------------------------
    # PUBLICATION INFORMATION
    # --------------------------------------------------------

    canvas.setFont(
        FONT_REGULAR,
        8,
    )

    canvas.drawString(
        LEFT_MARGIN,
        current_y,
        publication_date_text,
    )

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        current_y,
        edition_code,
    )

    current_y -= 8 * mm

    # --------------------------------------------------------
    # DIVIDER
    # --------------------------------------------------------

    canvas.setLineWidth(
        0.5
    )

    canvas.line(
        LEFT_MARGIN,
        current_y,
        PAGE_WIDTH - RIGHT_MARGIN,
        current_y,
    )

    current_y -= 9 * mm

    # --------------------------------------------------------
    # HEADING
    # --------------------------------------------------------

    canvas.setFont(
        FONT_BOLD,
        15,
    )

    canvas.drawString(
        LEFT_MARGIN,
        current_y,
        editorial["heading"],
    )

    gs_paper = editorial["gs_paper"]

    canvas.setFont(
        FONT_BOLD,
        9,
    )

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        current_y,
        gs_paper,
    )

    current_y -= 10 * mm

    # --------------------------------------------------------
    # POINTS
    # --------------------------------------------------------

    points = editorial.get(
        "points",
        []
    )

    if len(points) != 4:
        raise ValueError(
            f"Editorial {editorial.get('editorial_number')} "
            f"must contain exactly 4 points."
        )

    for point in points:

        paragraph = make_point_paragraph(
            number=point["number"],
            text=point["text"],
            anchor=point["anchor"],
            font_size=POINT_TEXT_SIZE,
            leading=POINT_TEXT_LEADING,
        )

        current_y = draw_paragraph(
            paragraph,
            canvas,
            x=LEFT_MARGIN,
            top=current_y,
            width=CONTENT_WIDTH,
        )

        current_y -= 5 * mm

    # --------------------------------------------------------
    # TAKEAWAY
    # --------------------------------------------------------

    current_y -= 2 * mm

    takeaway = make_takeaway_paragraph(
        editorial["takeaway"],
        font_size=TAKEAWAY_SIZE,
        leading=TAKEAWAY_LEADING,
    )

    current_y = draw_paragraph(
        takeaway,
        canvas,
        x=LEFT_MARGIN,
        top=current_y,
        width=CONTENT_WIDTH,
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer_y = (
        BOTTOM_MARGIN
        - 2 * mm
    )

    canvas.setFont(
        FONT_REGULAR,
        7,
    )

    canvas.drawString(
        LEFT_MARGIN,
        footer_y,
        "ONEPAGE STUDY",
    )

    editorial_number = editorial[
        "editorial_number"
    ]

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        footer_y,
        (
            f"{edition_code} • "
            f"Editorial {editorial_number}"
        ),
    )

    canvas.save()

    return output_path


# ============================================================
# BUILD REPOSITORY
# ============================================================

def build_repository() -> list[Path]:

    data = load_input()

    publication_date_text = data[
        "publication_date"
    ]

    publication_date = (
        parse_publication_date(
            publication_date_text
        )
    )

    date_code = publication_date.strftime(
        "%y%m%d"
    )

    edition_code = (
        f"UAK-ED-{date_code}"
    )

    editorials = data.get(
        "editorials",
        []
    )

    if not editorials:
        raise ValueError(
            "No editorials were found in INPUT.json."
        )

    generated_files: list[Path] = []

    for editorial in editorials:

        editorial_number = int(
            editorial["editorial_number"]
        )

        gs_folder = get_gs_folder(
            editorial["gs_paper"]
        )

        output_path = (
            build_repository_path(
                publication_date=publication_date,
                gs_folder=gs_folder,
                editorial_number=editorial_number,
            )
        )

        generated_pdf = (
            generate_editorial_pdf(
                editorial=editorial,
                publication_date_text=(
                    publication_date_text
                ),
                edition_code=edition_code,
                output_path=output_path,
            )
        )

        generated_files.append(
            generated_pdf
        )

        print(
            f"Editorial {editorial_number} "
            f"-> {gs_folder}"
        )

        print(
            f"Saved: {generated_pdf}"
        )

    return generated_files


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    register_fonts()

    print()
    print(
        "=" * 72
    )
    print(
        "BUILDING EDITORIAL REPOSITORY"
    )
    print(
        "=" * 72
    )

    generated_files = (
        build_repository()
    )

    print()
    print(
        "=" * 72
    )
    print(
        "EDITORIAL REPOSITORY COMPLETE"
    )
    print(
        "=" * 72
    )

    print(
        f"Editorial PDFs generated: "
        f"{len(generated_files)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )