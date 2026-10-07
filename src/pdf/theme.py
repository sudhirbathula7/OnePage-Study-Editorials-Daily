from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import mm


# ============================================================
# ONEPAGE STUDY • EDITORIALS DAILY
# PDF THEME
# ============================================================


# ============================================================
# COLOURS
# ============================================================

BLACK: Final[Color] = HexColor("#111827")
TEXT_BLACK: Final[Color] = HexColor("#172033")

HEADING_BLUE: Final[Color] = HexColor("#102A5C")

DARK_GREY: Final[Color] = HexColor("#4B5563")
MEDIUM_GREY: Final[Color] = HexColor("#7A8699")

LIGHT_GREY: Final[Color] = HexColor("#B8C5D8")
VERY_LIGHT_GREY: Final[Color] = HexColor("#E7ECF3")

WHITE: Final[Color] = HexColor("#FFFFFF")


# ============================================================
# COMPATIBILITY COLOURS
# ============================================================

# Retained for compatibility with existing components.

NAVY: Final[Color] = HEADING_BLUE
DARK_NAVY: Final[Color] = HEADING_BLUE

BORDER_GREY: Final[Color] = LIGHT_GREY
LIGHT_BORDER: Final[Color] = LIGHT_GREY
DIVIDER_GREY: Final[Color] = LIGHT_GREY

ANSWER_BLUE: Final[Color] = HEADING_BLUE
LIGHT_BLUE: Final[Color] = WHITE
OFF_WHITE: Final[Color] = WHITE


# ============================================================
# FONTS
# ============================================================

FONT_REGULAR: Final[str] = "Calibri"
FONT_BOLD: Final[str] = "Calibri-Bold"
FONT_ITALIC: Final[str] = "Calibri-Italic"
FONT_BOLD_ITALIC: Final[str] = "Calibri-BoldItalic"

FONT_OBLIQUE: Final[str] = FONT_ITALIC
FONT_BOLD_OBLIQUE: Final[str] = FONT_BOLD_ITALIC


# ============================================================
# HEADER
# ============================================================

# Existing header appearance remains unchanged.

HEADER_TITLE_SIZE: Final[float] = 19

HEADER_TITLE_SIZE_FULL: Final[float] = (
    HEADER_TITLE_SIZE
)

HEADER_TITLE_SIZE_HALF: Final[float] = (
    HEADER_TITLE_SIZE
)

HEADER_SUBTITLE_SIZE: Final[float] = 9
HEADER_DATE_LABEL_SIZE: Final[float] = 9
HEADER_DATE_SIZE: Final[float] = 9
HEADER_CODE_SIZE: Final[float] = 9

HEADER_RADIUS: Final[float] = 2 * mm


# ============================================================
# EDITORIAL HEADING
# ============================================================

# Stronger visual hierarchy than the first test PDF.

EDITORIAL_HEADING_SIZE: Final[float] = 12.5

EDITORIAL_GS_SIZE: Final[float] = 7.5

EDITORIAL_NUMBER_SIZE: Final[float] = 12


# ============================================================
# EDITORIAL POINTS
# ============================================================

# Preferred/default typography.
#
# The PDF generator can automatically reduce these values
# when an unusually long editorial needs more space.

POINT_NUMBER_SIZE: Final[float] = 10.5

POINT_TEXT_SIZE: Final[float] = 10.5

POINT_TEXT_LEADING: Final[float] = 12

POINT_GAP: Final[float] = 2.6 * mm


# ============================================================
# TAKEAWAY
# ============================================================

TAKEAWAY_SIZE: Final[float] = 10.5

TAKEAWAY_LEADING: Final[float] = 12

TAKEAWAY_TOP_GAP: Final[float] = 3.2 * mm


# ============================================================
# EDITORIAL BOX SPACING
# ============================================================

# Keep enough side padding for clean reading while making
# better use of the large editorial boxes.

EDITORIAL_PADDING_X: Final[float] = 4 * mm

EDITORIAL_PADDING_Y: Final[float] = 3.5 * mm

EDITORIAL_CONTENT_GAP: Final[float] = 2.6 * mm

EDITORIAL_HEADING_HEIGHT: Final[float] = 5.5 * mm


# ============================================================
# PAGE / GRID SPACING
# ============================================================

PAGE_SECTION_GAP: Final[float] = 1.2 * mm

EDITORIAL_COLUMN_GAP: Final[float] = 1.2 * mm

EDITORIAL_ROW_GAP: Final[float] = 1.2 * mm


# ============================================================
# BORDERS AND SHAPES
# ============================================================

BOX_RADIUS: Final[float] = 2 * mm

BOX_BORDER_WIDTH: Final[float] = 0.42

DIVIDER_WIDTH: Final[float] = 0.35

OUTER_BORDER_WIDTH: Final[float] = 0.45

INNER_BORDER_WIDTH: Final[float] = (
    BOX_BORDER_WIDTH
)

ICON_STROKE: Final[float] = 1.1

ICON_STROKE_WIDTH: Final[float] = (
    ICON_STROKE
)


# ============================================================
# GENERAL PADDING
# ============================================================

BOX_PADDING_X: Final[float] = 4 * mm

BOX_PADDING_Y: Final[float] = 3 * mm

TEXT_PADDING: Final[float] = 2 * mm

COLUMN_GAP: Final[float] = 2 * mm


# ============================================================
# FOOTER
# ============================================================

# Existing footer appearance remains unchanged.

FOOTER_SIZE: Final[float] = 7


# ============================================================
# AUTOMATIC TEXT-FIT LIMITS
# ============================================================

# These are rendering safeguards only.
#
# They do NOT impose word-count rules on the input.
#
# Normal editorials should render at the larger preferred
# sizes above. The generator only moves toward these minimums
# when the content cannot otherwise fit.

MIN_POINT_TEXT_SIZE: Final[float] = 8.25

MIN_POINT_TEXT_LEADING: Final[float] = 9.5

MIN_TAKEAWAY_SIZE: Final[float] = 8.25

MIN_TAKEAWAY_LEADING: Final[float] = 9.5


# ============================================================
# THEME OBJECT
# ============================================================

@dataclass(frozen=True)
class Theme:
    text: Color = TEXT_BLACK
    heading: Color = HEADING_BLUE
    border: Color = LIGHT_GREY
    divider: Color = LIGHT_GREY
    background: Color = WHITE

    regular_font: str = FONT_REGULAR
    bold_font: str = FONT_BOLD
    italic_font: str = FONT_ITALIC
    bold_italic_font: str = FONT_BOLD_ITALIC


THEME = Theme()