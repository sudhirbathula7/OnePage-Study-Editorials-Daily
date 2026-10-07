from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import (
    registerFontFamily,
    stringWidth,
)
from reportlab.platypus import Paragraph

from src.pdf.page_setup import Rect
from src.pdf.theme import (
    FONT_BOLD,
    FONT_BOLD_ITALIC,
    FONT_ITALIC,
    FONT_REGULAR,
    TEXT_BLACK,
)


# ============================================================
# ONEPAGE STUDY • EDITORIALS DAILY
# PDF HELPERS
# ============================================================


# ============================================================
# TEXT FIT RESULT
# ============================================================

@dataclass(frozen=True, slots=True)
class TextFitResult:
    fits: bool
    width: float
    height: float
    available_height: float


# ============================================================
# FONT FAMILY
# ============================================================

def register_paragraph_fonts() -> None:
    """
    Register the Calibri family for ReportLab Paragraph markup.

    This should be called after font_loader.register_fonts().
    """

    registerFontFamily(
        FONT_REGULAR,
        normal=FONT_REGULAR,
        bold=FONT_BOLD,
        italic=FONT_ITALIC,
        boldItalic=FONT_BOLD_ITALIC,
    )


# ============================================================
# BASIC CANVAS TEXT
# ============================================================

def draw_text(
    canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: float,
    color=TEXT_BLACK,
) -> None:
    """
    Draw left-aligned single-line text.
    """

    canvas.saveState()

    canvas.setFillColor(color)

    canvas.setFont(
        font_name,
        font_size,
    )

    canvas.drawString(
        x,
        y,
        text,
    )

    canvas.restoreState()


def draw_centered_text(
    canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: float,
    color=TEXT_BLACK,
) -> None:
    """
    Draw centered single-line text.
    """

    canvas.saveState()

    canvas.setFillColor(color)

    canvas.setFont(
        font_name,
        font_size,
    )

    canvas.drawCentredString(
        x,
        y,
        text,
    )

    canvas.restoreState()


def draw_right_text(
    canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: float,
    color=TEXT_BLACK,
) -> None:
    """
    Draw right-aligned single-line text.
    """

    canvas.saveState()

    canvas.setFillColor(color)

    canvas.setFont(
        font_name,
        font_size,
    )

    canvas.drawRightString(
        x,
        y,
        text,
    )

    canvas.restoreState()


# ============================================================
# SINGLE-LINE FONT FITTING
# ============================================================

def fit_font_size(
    text: str,
    font_name: str,
    preferred_size: float,
    available_width: float,
    minimum_size: float,
) -> float:
    """
    Reduce font size only when necessary to fit one line.
    """

    if available_width <= 0:
        return minimum_size

    current_size = preferred_size

    while current_size > minimum_size:

        width = stringWidth(
            text,
            font_name,
            current_size,
        )

        if width <= available_width:
            return current_size

        current_size -= 0.25

    return minimum_size


# ============================================================
# SAFE PARAGRAPH TEXT
# ============================================================

def escape_pdf_text(
    text: str,
) -> str:
    """
    Escape XML-sensitive characters before passing text
    into a ReportLab Paragraph.
    """

    return escape(
        str(text),
        quote=False,
    )


# ============================================================
# RECALL ANCHOR HIGHLIGHTING
# ============================================================

def highlight_anchor(
    text: str,
    anchor: str,
) -> str:
    """
    Bold the manually selected Recall Anchor inside the point.

    The original point wording is never changed.
    """

    clean_anchor = anchor.strip()

    if not clean_anchor:
        return escape_pdf_text(text)

    match = re.search(
        re.escape(clean_anchor),
        text,
        flags=re.IGNORECASE,
    )

    if match is None:
        raise ValueError(
            "Recall Anchor was not found inside its "
            f"corresponding point: {anchor!r}"
        )

    before = escape_pdf_text(
        text[:match.start()]
    )

    selected = escape_pdf_text(
        text[
            match.start():
            match.end()
        ]
    )

    after = escape_pdf_text(
        text[match.end():]
    )

    return (
        before
        + f"<b>{selected}</b>"
        + after
    )


# ============================================================
# PARAGRAPH STYLE
# ============================================================

def make_paragraph_style(
    name: str,
    *,
    font_name: str = FONT_REGULAR,
    font_size: float = 9,
    leading: float = 10.5,
    alignment: int = TA_LEFT,
    text_color=TEXT_BLACK,
    left_indent: float = 0,
    right_indent: float = 0,
    first_line_indent: float = 0,
) -> ParagraphStyle:
    """
    Create a compact paragraph style.
    """

    return ParagraphStyle(
        name=name,
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        alignment=alignment,
        textColor=text_color,
        leftIndent=left_indent,
        rightIndent=right_indent,
        firstLineIndent=first_line_indent,
        spaceBefore=0,
        spaceAfter=0,
        allowWidows=0,
        allowOrphans=0,
        splitLongWords=1,
    )


# ============================================================
# PARAGRAPH CREATION
# ============================================================

def make_paragraph(
    text: str,
    style: ParagraphStyle,
    *,
    markup: bool = False,
) -> Paragraph:
    """
    Create a ReportLab Paragraph.
    """

    content = (
        text
        if markup
        else escape_pdf_text(text)
    )

    return Paragraph(
        content,
        style,
    )


# ============================================================
# PARAGRAPH MEASUREMENT
# ============================================================

def measure_paragraph(
    paragraph: Paragraph,
    available_width: float,
) -> tuple[float, float]:
    """
    Return wrapped paragraph width and height.
    """

    return paragraph.wrap(
        max(
            1,
            available_width,
        ),
        100000,
    )


# ============================================================
# PARAGRAPH DRAWING
# ============================================================

def draw_paragraph(
    canvas,
    paragraph: Paragraph,
    *,
    x: float,
    top: float,
    available_width: float,
) -> float:
    """
    Draw a paragraph downward from a top coordinate.

    Returns the Y coordinate immediately below it.
    """

    _, height = measure_paragraph(
        paragraph,
        available_width,
    )

    paragraph.drawOn(
        canvas,
        x,
        top - height,
    )

    return top - height


# ============================================================
# FIT CHECK
# ============================================================

def check_text_fit(
    paragraph: Paragraph,
    rect: Rect,
) -> TextFitResult:
    """
    Check whether a paragraph fits inside a rectangle.
    """

    width, height = measure_paragraph(
        paragraph,
        rect.width,
    )

    return TextFitResult(
        fits=height <= rect.height,
        width=width,
        height=height,
        available_height=rect.height,
    )


# ============================================================
# EDITORIAL BULLET POINT
# ============================================================

def make_point_paragraph(
    number: int,
    text: str,
    anchor: str,
    *,
    font_size: float = 9,
    leading: float = 10.5,
) -> Paragraph:
    """
    Create one editorial bullet point.

    The point number is retained in the data model but is
    intentionally not displayed in the PDF.

    Visible form:

        • Editorial explanation with the selected
          Recall Anchor bolded inside the point.
    """

    # `number` remains intentionally accepted because the
    # structured input still identifies Point 1–4.
    _ = number

    style = make_paragraph_style(
        name=f"EditorialBullet{number}",
        font_name=FONT_REGULAR,
        font_size=font_size,
        leading=leading,
        alignment=TA_LEFT,

        # Hanging indent:
        # bullet stays on the left while wrapped lines align
        # with the beginning of the point text.
        left_indent=4.2 * mm,
        first_line_indent=-4.2 * mm,
    )

    highlighted_text = highlight_anchor(
        text,
        anchor,
    )

    markup = (
        f'<font name="{FONT_BOLD}">'
        f"•"
        f"</font>"
        f"&nbsp;&nbsp;"
        f"{highlighted_text}"
    )

    return make_paragraph(
        markup,
        style,
        markup=True,
    )


# ============================================================
# TAKEAWAY
# ============================================================

def make_takeaway_paragraph(
    text: str,
    *,
    font_size: float = 9,
    leading: float = 11,
) -> Paragraph:
    """
    Create the final Takeaway.

    Visible treatment:
    - bold
    - italic
    - centered
    - no 'KEY TAKEAWAY' label
    """

    style = make_paragraph_style(
        name="EditorialTakeaway",
        font_name=FONT_BOLD_ITALIC,
        font_size=font_size,
        leading=leading,
        alignment=TA_CENTER,
    )

    return make_paragraph(
        text,
        style,
    )


# ============================================================
# TOTAL PARAGRAPH HEIGHT
# ============================================================

def total_paragraph_height(
    paragraphs: tuple[Paragraph, ...],
    available_width: float,
    *,
    gap: float = 0,
) -> float:
    """
    Calculate the total wrapped height of several paragraphs.
    """

    if not paragraphs:
        return 0

    total_height = 0.0

    for paragraph in paragraphs:

        _, paragraph_height = measure_paragraph(
            paragraph,
            available_width,
        )

        total_height += paragraph_height

    if len(paragraphs) > 1:
        total_height += (
            gap
            * (len(paragraphs) - 1)
        )

    return total_height