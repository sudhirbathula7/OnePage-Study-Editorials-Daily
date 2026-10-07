from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

from src.config import (
    CONTENT_HEIGHT,
    CONTENT_WIDTH,
    PAGE_MARGIN_BOTTOM,
    PAGE_MARGIN_LEFT,
)


# ============================================================
# ONEPAGE STUDY — EDITORIALS DAILY
# PAGE SETUP
# ============================================================


# ============================================================
# PAGE SIZE
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4


# ============================================================
# RECTANGLE
# ============================================================

@dataclass(frozen=True, slots=True)
class Rect:
    """
    Simple immutable rectangle used throughout the PDF system.

    ReportLab coordinates begin at the bottom-left corner
    of the page.
    """

    x: float
    y: float
    width: float
    height: float

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y

    @property
    def top(self) -> float:
        return self.y + self.height

    # --------------------------------------------------------
    # CENTRE
    # --------------------------------------------------------

    @property
    def center_x(self) -> float:
        return self.x + (self.width / 2)

    @property
    def center_y(self) -> float:
        return self.y + (self.height / 2)

    # Existing header/footer use British spelling.
    # Keep these aliases for compatibility.

    @property
    def centre_x(self) -> float:
        return self.center_x

    @property
    def centre_y(self) -> float:
        return self.center_y

    # --------------------------------------------------------
    # INSET
    # --------------------------------------------------------

    def inset(
        self,
        x_amount: float,
        y_amount: float | None = None,
    ) -> "Rect":
        """
        Return a rectangle inset from all four sides.

        If y_amount is omitted, x_amount is used for both
        horizontal and vertical inset.
        """

        resolved_y = (
            x_amount
            if y_amount is None
            else y_amount
        )

        return Rect(
            x=self.x + x_amount,
            y=self.y + resolved_y,
            width=max(
                0,
                self.width - (2 * x_amount),
            ),
            height=max(
                0,
                self.height - (2 * resolved_y),
            ),
        )

    # --------------------------------------------------------
    # VERTICAL SPLIT
    # --------------------------------------------------------

    def split_vertical(
        self,
        left_ratio: float = 0.5,
        gap: float = 0,
    ) -> tuple["Rect", "Rect"]:
        """
        Split this rectangle into left and right rectangles.
        """

        usable_width = max(
            0,
            self.width - gap,
        )

        left_width = (
            usable_width * left_ratio
        )

        right_width = (
            usable_width - left_width
        )

        left = Rect(
            x=self.x,
            y=self.y,
            width=left_width,
            height=self.height,
        )

        right = Rect(
            x=left.right + gap,
            y=self.y,
            width=right_width,
            height=self.height,
        )

        return left, right

    # --------------------------------------------------------
    # HORIZONTAL SPLIT
    # --------------------------------------------------------

    def split_horizontal(
        self,
        top_ratio: float = 0.5,
        gap: float = 0,
    ) -> tuple["Rect", "Rect"]:
        """
        Split this rectangle into top and bottom rectangles.
        """

        usable_height = max(
            0,
            self.height - gap,
        )

        top_height = (
            usable_height * top_ratio
        )

        bottom_height = (
            usable_height - top_height
        )

        bottom = Rect(
            x=self.x,
            y=self.y,
            width=self.width,
            height=bottom_height,
        )

        top = Rect(
            x=self.x,
            y=bottom.top + gap,
            width=self.width,
            height=top_height,
        )

        return top, bottom


# ============================================================
# CONTENT AREA
# ============================================================

def get_content_rect() -> Rect:
    """
    Return the usable page area defined by src.config.

    This preserves the page margins already established
    in the original project.
    """

    return Rect(
        x=PAGE_MARGIN_LEFT,
        y=PAGE_MARGIN_BOTTOM,
        width=CONTENT_WIDTH,
        height=CONTENT_HEIGHT,
    )


# ============================================================
# CANVAS
# ============================================================

def create_canvas(
    output_path: str | Path,
) -> Canvas:
    """
    Create an A4 ReportLab canvas.
    """

    return Canvas(
        str(output_path),
        pagesize=A4,
        pageCompression=1,
    )


# ============================================================
# PAGE LIFECYCLE
# ============================================================

def begin_page(
    canvas: Canvas,
) -> None:
    """
    Prepare a page for rendering.

    This function is intentionally lightweight so that
    page-wide behaviour can be added later without changing
    the PDF generator.
    """

    canvas.saveState()
    canvas.restoreState()


def finish_page(
    canvas: Canvas,
) -> None:
    """
    Finish the current page.
    """

    canvas.showPage()