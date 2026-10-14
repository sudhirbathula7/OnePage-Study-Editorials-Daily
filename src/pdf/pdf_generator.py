from __future__ import annotations

import math
import json
from xml.sax.saxutils import escape

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pathlib import Path

from reportlab.lib.units import mm

from src.components.footer import (
    FooterData,
    draw_footer,
)
from src.components.header import (
    HeaderData,
    draw_header,
)
from src.knowledge_engine.knowledge_loader import (
    EditorialRecord,
    EditorialStudyData,
    load_editorial_study_data,
)
from src.pdf.helpers import (
    draw_paragraph,
    draw_text,
    fit_font_size,
    make_point_paragraph,
    make_takeaway_paragraph,
    measure_paragraph,
)
from src.pdf.layout import (
    SHOW_EDITORIAL_BOXES,
    SHOW_FOOTER,
    SHOW_HEADER,
    draw_editorial_box,
    get_page_layout,
)
from src.pdf.page_setup import (
    Rect,
    begin_page,
    create_canvas,
    finish_page,
)
from src.pdf.theme import (
    DARK_GREY,
    EDITORIAL_GS_SIZE,
    EDITORIAL_HEADING_SIZE,
    EDITORIAL_PADDING_X,
    EDITORIAL_PADDING_Y,
    FONT_BOLD,
    MIN_POINT_TEXT_LEADING,
    MIN_POINT_TEXT_SIZE,
    MIN_TAKEAWAY_LEADING,
    MIN_TAKEAWAY_SIZE,
    POINT_GAP,
    POINT_TEXT_LEADING,
    POINT_TEXT_SIZE,
    TAKEAWAY_LEADING,
    TAKEAWAY_SIZE,
    TEXT_BLACK,
)
from src.publication import (
    PublicationMetadata,
    build_publication_metadata,
)


# ============================================================
# ONEPAGE STUDY • EDITORIALS DAILY
# PDF GENERATOR
# ============================================================


# ============================================================
# EDITORIAL SPACING
# ============================================================

# Small tab-like indent for the editorial heading.
HEADING_LEFT_INDENT = 2 * mm

# Extra breathing room between the top of the editorial box
# and the heading.
BOX_TO_HEADING_GAP = 2 * mm

# Space between editorial heading and Point 1.
HEADING_TO_FIRST_POINT_GAP = 4 * mm

# Space between Point 4 and the Takeaway.
LAST_POINT_TO_TAKEAWAY_GAP = 3 * mm


# ============================================================
# EDITORIAL FIT SETTINGS
# ============================================================

POINT_SIZE_STEP = 0.25
POINT_LEADING_STEP = 0.25

TAKEAWAY_SIZE_STEP = 0.25
TAKEAWAY_LEADING_STEP = 0.25


# ============================================================
# EDITORIAL HEADING
# ============================================================

def _draw_editorial_heading(
    canvas,
    rect: Rect,
    editorial: EditorialRecord,
) -> float:
    """Place question (left 85%) and GS label (right 15%) on one row."""
    question = _question_for_heading(editorial.heading)
    gs_text = editorial.gs_paper.strip()

    heading_x = rect.x + HEADING_LEFT_INDENT
    heading_top = rect.top - BOX_TO_HEADING_GAP
    total_width = rect.right - heading_x
    gs_width = total_width * 0.15
    question_width = total_width * 0.85 - 2 * mm

    question_size = min(EDITORIAL_HEADING_SIZE, 10.0)
    style = ParagraphStyle(
        "EditorialQuestion",
        fontName=FONT_BOLD,
        fontSize=question_size,
        leading=question_size + 2,
        textColor=TEXT_BLACK,
        spaceBefore=0,
        spaceAfter=0,
        splitLongWords=True,
    )
    paragraph = Paragraph(escape(question), style)
    _, question_height = paragraph.wrap(question_width, rect.height)
    paragraph.drawOn(canvas, heading_x, heading_top - question_height)

    gs_size = fit_font_size(
        text=gs_text,
        font_name=FONT_BOLD,
        preferred_size=EDITORIAL_GS_SIZE,
        available_width=gs_width,
        minimum_size=5.5,
    )
    canvas.saveState()
    canvas.setFillColor(DARK_GREY)
    canvas.setFont(FONT_BOLD, gs_size)
    # Align the GS baseline with the first question line.
    gs_baseline = heading_top - question_size
    canvas.drawRightString(rect.right, gs_baseline, gs_text)
    canvas.restoreState()

    heading_height = max(question_height, question_size + 2)
    return heading_top - heading_height - HEADING_TO_FIRST_POINT_GAP


def _question_for_heading(heading: str) -> str:
    """Use the exact question from INPUT.json; never invent one."""
    input_path = Path(__file__).resolve().parents[2] / "input_processing" / "INPUT.json"
    with input_path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    matches = [
        item for item in data["editorials"]
        if item.get("heading") == heading
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one INPUT.json editorial with heading {heading!r}; "
            f"found {len(matches)}."
        )
    question = matches[0].get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"Missing question for editorial {heading!r}")
    return question.strip()


# ============================================================
# EDITORIAL CONTENT MEASUREMENT
# ============================================================

def _measure_editorial_content(
    editorial: EditorialRecord,
    available_width: float,
    point_font_size: float,
    point_leading: float,
    takeaway_font_size: float,
    takeaway_leading: float,
) -> tuple[
    tuple,
    object,
    float,
]:
    """
    Build the four points and Takeaway and calculate
    their total required height.
    """

    point_paragraphs = tuple(
        make_point_paragraph(
            number=point.number,
            text=point.text,
            anchor=point.anchor,
            font_size=point_font_size,
            leading=point_leading,
        )
        for point in editorial.points
    )

    takeaway_paragraph = (
        make_takeaway_paragraph(
            editorial.takeaway,
            font_size=takeaway_font_size,
            leading=takeaway_leading,
        )
    )

    total_height = 0.0

    # --------------------------------------------------------
    # POINTS 1–4
    # --------------------------------------------------------

    for index, paragraph in enumerate(
        point_paragraphs
    ):
        _, paragraph_height = (
            measure_paragraph(
                paragraph,
                available_width,
            )
        )

        total_height += (
            paragraph_height
        )

        if (
            index
            < len(point_paragraphs) - 1
        ):
            total_height += (
                POINT_GAP
            )

    # --------------------------------------------------------
    # POINT 4 → TAKEAWAY
    # --------------------------------------------------------

    _, takeaway_height = (
        measure_paragraph(
            takeaway_paragraph,
            available_width,
        )
    )

    total_height += (
        LAST_POINT_TO_TAKEAWAY_GAP
        + takeaway_height
    )

    return (
        point_paragraphs,
        takeaway_paragraph,
        total_height,
    )


# ============================================================
# AUTOMATIC EDITORIAL FITTING
# ============================================================

def _fit_editorial_content(
    editorial: EditorialRecord,
    available_width: float,
    available_height: float,
):
    """
    Use the preferred typography whenever possible.

    If an editorial is unusually long, reduce typography
    gradually until it fits.

    This is only a PDF rendering safeguard and does not impose
    content word-count restrictions.
    """

    point_size = (
        POINT_TEXT_SIZE
    )

    point_leading = (
        POINT_TEXT_LEADING
    )

    takeaway_size = (
        TAKEAWAY_SIZE
    )

    takeaway_leading = (
        TAKEAWAY_LEADING
    )

    while True:

        (
            point_paragraphs,
            takeaway_paragraph,
            total_height,
        ) = _measure_editorial_content(
            editorial=editorial,
            available_width=available_width,
            point_font_size=point_size,
            point_leading=point_leading,
            takeaway_font_size=takeaway_size,
            takeaway_leading=takeaway_leading,
        )

        # ----------------------------------------------------
        # FITS
        # ----------------------------------------------------

        if total_height <= available_height:
            return (
                point_paragraphs,
                takeaway_paragraph,
            )

        changed = False

        # ----------------------------------------------------
        # POINT FONT
        # ----------------------------------------------------

        if (
            point_size
            > MIN_POINT_TEXT_SIZE
        ):
            point_size = max(
                MIN_POINT_TEXT_SIZE,
                point_size
                - POINT_SIZE_STEP,
            )

            changed = True

        # ----------------------------------------------------
        # POINT LEADING
        # ----------------------------------------------------

        if (
            point_leading
            > MIN_POINT_TEXT_LEADING
        ):
            point_leading = max(
                MIN_POINT_TEXT_LEADING,
                point_leading
                - POINT_LEADING_STEP,
            )

            changed = True

        # ----------------------------------------------------
        # TAKEAWAY FONT
        # ----------------------------------------------------

        if (
            takeaway_size
            > MIN_TAKEAWAY_SIZE
        ):
            takeaway_size = max(
                MIN_TAKEAWAY_SIZE,
                takeaway_size
                - TAKEAWAY_SIZE_STEP,
            )

            changed = True

        # ----------------------------------------------------
        # TAKEAWAY LEADING
        # ----------------------------------------------------

        if (
            takeaway_leading
            > MIN_TAKEAWAY_LEADING
        ):
            takeaway_leading = max(
                MIN_TAKEAWAY_LEADING,
                takeaway_leading
                - TAKEAWAY_LEADING_STEP,
            )

            changed = True

        # ----------------------------------------------------
        # CANNOT FIT
        # ----------------------------------------------------

        if not changed:
            raise ValueError(
                "\nEditorial content does not fit inside "
                "its OnePage Study box even at the minimum "
                "PDF typography.\n\n"
                f"Editorial: {editorial.heading}\n\n"
                "The editorial content has not been changed. "
                "Shorten the content slightly or adjust the "
                "PDF layout."
            )


# ============================================================
# SINGLE EDITORIAL
# ============================================================

def _draw_editorial(
    canvas,
    rect: Rect,
    editorial: EditorialRecord,
) -> None:
    """
    Draw one editorial:

        Heading                              GS II

        1. Point
        2. Point
        3. Point
        4. Point

             Takeaway

    The Core Question remains hidden.

    Recall Anchors are bolded inside their corresponding
    points.

    Editorial numbering is not displayed.
    """

    # --------------------------------------------------------
    # OUTER BOX
    # --------------------------------------------------------

    if SHOW_EDITORIAL_BOXES:
        draw_editorial_box(
            canvas=canvas,
            rect=rect,
        )

    # --------------------------------------------------------
    # INNER CONTENT AREA
    # --------------------------------------------------------

    content_rect = Rect(
        x=(
            rect.x
            + EDITORIAL_PADDING_X
        ),
        y=(
            rect.y
            + EDITORIAL_PADDING_Y
        ),
        width=max(
            0,
            rect.width
            - (
                2
                * EDITORIAL_PADDING_X
            ),
        ),
        height=max(
            0,
            rect.height
            - (
                2
                * EDITORIAL_PADDING_Y
            ),
        ),
    )

    # --------------------------------------------------------
    # HEADING
    # --------------------------------------------------------

    body_top = (
        _draw_editorial_heading(
            canvas=canvas,
            rect=content_rect,
            editorial=editorial,
        )
    )

    # --------------------------------------------------------
    # AVAILABLE BODY HEIGHT
    # --------------------------------------------------------

    body_height = max(
        0,
        body_top
        - content_rect.y,
    )

    # --------------------------------------------------------
    # FIT CONTENT
    # --------------------------------------------------------

    (
        point_paragraphs,
        takeaway_paragraph,
    ) = _fit_editorial_content(
        editorial=editorial,
        available_width=content_rect.width,
        available_height=body_height,
    )

    current_top = (
        body_top
    )

    # --------------------------------------------------------
    # POINTS 1–4
    # --------------------------------------------------------

    for index, paragraph in enumerate(
        point_paragraphs
    ):

        current_top = draw_paragraph(
            canvas=canvas,
            paragraph=paragraph,
            x=content_rect.x,
            top=current_top,
            available_width=(
                content_rect.width
            ),
        )

        if (
            index
            < len(point_paragraphs) - 1
        ):
            current_top -= (
                POINT_GAP
            )

    # --------------------------------------------------------
    # POINT 4 → TAKEAWAY
    # --------------------------------------------------------

    current_top -= (
        LAST_POINT_TO_TAKEAWAY_GAP
    )

    draw_paragraph(
        canvas=canvas,
        paragraph=takeaway_paragraph,
        x=content_rect.x,
        top=current_top,
        available_width=(
            content_rect.width
        ),
    )


# ============================================================
# PAGE RENDERER
# ============================================================

def _draw_editorial_page(
    canvas,
    editorials: tuple[EditorialRecord, ...],
    page_number: int,
    total_pages: int,
    metadata: PublicationMetadata,
) -> None:
    """
    Draw one A4 page containing up to four editorials.
    """

    begin_page(
        canvas
    )

    layout = (
        get_page_layout()
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    if SHOW_HEADER:
        draw_header(
            canvas=canvas,
            rect=layout.header,
            data=HeaderData(
                title=metadata.title,
                subtitle=metadata.subtitle,
                publication_date=(
                    metadata.publication_date
                ),
                edition_code=(
                    metadata.edition_code
                ),
            ),
            compact=False,
        )

    # --------------------------------------------------------
    # EDITORIAL GRID
    # --------------------------------------------------------

    for editorial, editorial_rect in zip(
        editorials,
        layout.editorial_rects,
    ):
        _draw_editorial(
            canvas=canvas,
            rect=editorial_rect,
            editorial=editorial,
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    if SHOW_FOOTER:
        draw_footer(
            canvas=canvas,
            rect=layout.footer,
            data=FooterData(
                brand_name=(
                    metadata.footer_brand
                ),
                publication_code=(
                    metadata.edition_code
                ),
                page_number=page_number,
                total_pages=total_pages,
            ),
        )

    finish_page(
        canvas
    )


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_pdf(
    output_path: Path,
    metadata: PublicationMetadata | None = None,
) -> Path:
    """
    Generate OnePage Study • Editorials Daily.

    Target:
        Four short editorials per A4 page.

    Fewer editorials are supported.

    More than four automatically continue onto additional
    pages.
    """

    study_data: EditorialStudyData = (
        load_editorial_study_data()
    )

    editorials = (
        study_data.editorials
    )

    if not editorials:
        raise ValueError(
            "No editorials were found in INPUT.json."
        )

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    resolved_metadata = (
        metadata
        if metadata is not None
        else build_publication_metadata()
    )

    # --------------------------------------------------------
    # OUTPUT PATH
    # --------------------------------------------------------

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    canvas = create_canvas(
        output_path
    )

    # --------------------------------------------------------
    # FOUR EDITORIALS PER PAGE
    # --------------------------------------------------------

    editorials_per_page = 4

    total_pages = math.ceil(
        len(editorials)
        / editorials_per_page
    )

    # --------------------------------------------------------
    # DRAW PAGES
    # --------------------------------------------------------

    for page_index in range(
        total_pages
    ):

        start_index = (
            page_index
            * editorials_per_page
        )

        end_index = (
            start_index
            + editorials_per_page
        )

        page_editorials = tuple(
            editorials[
                start_index:end_index
            ]
        )

        _draw_editorial_page(
            canvas=canvas,
            editorials=page_editorials,
            page_number=(
                page_index + 1
            ),
            total_pages=total_pages,
            metadata=resolved_metadata,
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    canvas.save()

    return output_path


# ============================================================
# PREVIEW
# ============================================================

def generate_pdf_preview(
    output_path: Path,
    metadata: PublicationMetadata | None = None,
) -> Path:
    """
    Preview uses exactly the same renderer as the final PDF.
    """

    return generate_pdf(
        output_path=output_path,
        metadata=metadata,
    )