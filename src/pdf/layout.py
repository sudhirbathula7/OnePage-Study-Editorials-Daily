from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from src.pdf.page_setup import (
    Rect,
    get_content_rect,
)
from src.pdf.theme import (
    BOX_BORDER_WIDTH,
    BOX_RADIUS,
    EDITORIAL_COLUMN_GAP,
    EDITORIAL_ROW_GAP,
    LIGHT_GREY,
    PAGE_SECTION_GAP,
    WHITE,
)


# ============================================================
# ONEPAGE STUDY — EDITORIALS DAILY
# PAGE LAYOUT
# ============================================================


# ============================================================
# DISPLAY SETTINGS
# ============================================================

SHOW_EDITORIAL_BOXES = True
SHOW_HEADER = True
SHOW_FOOTER = True


# ============================================================
# MAJOR PAGE DIMENSIONS
# ============================================================

# Preserve the compact header/footer proportions used by the
# existing project.

HEADER_HEIGHT = 12 * mm
FOOTER_HEIGHT = 6 * mm


# ============================================================
# PAGE LAYOUT MODEL
# ============================================================

@dataclass(frozen=True, slots=True)
class EditorialPageLayout:
    page: Rect

    header: Rect
    body: Rect
    footer: Rect

    editorial_1: Rect
    editorial_2: Rect
    editorial_3: Rect
    editorial_4: Rect

    @property
    def editorial_rects(
        self,
    ) -> tuple[Rect, Rect, Rect, Rect]:
        return (
            self.editorial_1,
            self.editorial_2,
            self.editorial_3,
            self.editorial_4,
        )


# ============================================================
# BUILD PAGE LAYOUT
# ============================================================

def build_page_layout() -> EditorialPageLayout:
    """
    Build the fixed A4 geometry for OnePage Study.

    Structure:

        Header

        Editorial 01 | Editorial 02
        -------------+-------------
        Editorial 03 | Editorial 04

        Footer

    The existing project content margins are preserved through
    get_content_rect().
    """

    page = get_content_rect()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = Rect(
        x=page.x,
        y=page.top - HEADER_HEIGHT,
        width=page.width,
        height=HEADER_HEIGHT,
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer = Rect(
        x=page.x,
        y=page.y,
        width=page.width,
        height=FOOTER_HEIGHT,
    )

    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    body_top = (
        header.y
        - PAGE_SECTION_GAP
    )

    body_bottom = (
        footer.top
        + PAGE_SECTION_GAP
    )

    body = Rect(
        x=page.x,
        y=body_bottom,
        width=page.width,
        height=max(
            0,
            body_top - body_bottom,
        ),
    )

    # --------------------------------------------------------
    # TWO ROWS
    # --------------------------------------------------------

    top_row, bottom_row = (
        body.split_horizontal(
            top_ratio=0.5,
            gap=EDITORIAL_ROW_GAP,
        )
    )

    # --------------------------------------------------------
    # TOP ROW
    # --------------------------------------------------------

    editorial_1, editorial_2 = (
        top_row.split_vertical(
            left_ratio=0.5,
            gap=EDITORIAL_COLUMN_GAP,
        )
    )

    # --------------------------------------------------------
    # BOTTOM ROW
    # --------------------------------------------------------

    editorial_3, editorial_4 = (
        bottom_row.split_vertical(
            left_ratio=0.5,
            gap=EDITORIAL_COLUMN_GAP,
        )
    )

    return EditorialPageLayout(
        page=page,
        header=header,
        body=body,
        footer=footer,
        editorial_1=editorial_1,
        editorial_2=editorial_2,
        editorial_3=editorial_3,
        editorial_4=editorial_4,
    )


# ============================================================
# EDITORIAL BOX
# ============================================================

def draw_editorial_box(
    canvas: Canvas,
    rect: Rect,
    *,
    enabled: bool | None = None,
) -> None:
    """
    Draw the rounded outer border for one editorial.

    Content rendering is intentionally kept out of this file.
    """

    should_draw = (
        SHOW_EDITORIAL_BOXES
        if enabled is None
        else enabled
    )

    if not should_draw:
        return

    canvas.saveState()

    canvas.setStrokeColor(
        LIGHT_GREY
    )

    canvas.setFillColor(
        WHITE
    )

    canvas.setLineWidth(
        BOX_BORDER_WIDTH
    )

    canvas.roundRect(
        rect.x,
        rect.y,
        rect.width,
        rect.height,
        BOX_RADIUS,
        stroke=1,
        fill=1,
    )

    canvas.restoreState()


# ============================================================
# LAYOUT ACCESSOR
# ============================================================

_PAGE_LAYOUT = build_page_layout()


def get_page_layout() -> EditorialPageLayout:
    """
    Return the fixed page geometry.
    """

    return _PAGE_LAYOUT