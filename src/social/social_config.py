from __future__ import annotations


# ============================================================
# ONEPAGE STUDY • EDITORIALS DAILY
# SOCIAL IMAGE CONFIGURATION
# ============================================================


# ============================================================
# CANVAS — 9:16 PHONE FORMAT
# ============================================================

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920

IMAGE_SIZE = (
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
)


# ============================================================
# SAFE VERTICAL AREA
# ============================================================

# Keep 10% empty at top and bottom.

TOP_SAFE_PERCENT = 0.10
BOTTOM_SAFE_PERCENT = 0.10

TOP_MARGIN = round(
    IMAGE_HEIGHT * TOP_SAFE_PERCENT
)

BOTTOM_MARGIN = round(
    IMAGE_HEIGHT * BOTTOM_SAFE_PERCENT
)

USABLE_TOP = TOP_MARGIN

USABLE_BOTTOM = (
    IMAGE_HEIGHT
    - BOTTOM_MARGIN
)

USABLE_HEIGHT = (
    USABLE_BOTTOM
    - USABLE_TOP
)


# ============================================================
# HORIZONTAL AREA
# ============================================================

LEFT_MARGIN = 55
RIGHT_MARGIN = 55

CONTENT_WIDTH = (
    IMAGE_WIDTH
    - LEFT_MARGIN
    - RIGHT_MARGIN
)


# ============================================================
# COLORS
# ============================================================

BACKGROUND_COLOR = "#FFFFFF"

PRIMARY_TEXT_COLOR = "#111827"

QUESTION_TEXT_COLOR = "#172033"

ANCHOR_TEXT_COLOR = "#274C77"

DATE_TEXT_COLOR = "#4B5563"

BRAND_TEXT_COLOR = "#111827"

HEADING_TEXT_COLOR = "#102A5C"

ANCHOR_DOT_COLOR = "#7A8699"


# ============================================================
# TOP BRAND ROW
# ============================================================

LOGO_WIDTH = 72
LOGO_HEIGHT = 72

LOGO_X = LEFT_MARGIN
LOGO_Y = USABLE_TOP

LOGO_BRAND_GAP = 20

BRAND_FONT_SIZE = 34

DATE_FONT_SIZE = 28


# ============================================================
# PRODUCT HEADING
# ============================================================

PRODUCT_HEADING = (
    "ONEPAGE STUDY • EDITORIALS DAILY"
)

PRODUCT_HEADING_FONT_SIZE = 47

TOP_ROW_TO_HEADING_GAP = 58

HEADING_TO_CONTENT_GAP = 70


# ============================================================
# QUESTIONS
# ============================================================

# Larger for phone readability.

QUESTION_FONT_SIZE = 48

QUESTION_LINE_SPACING = 12

QUESTION_MAX_WIDTH = CONTENT_WIDTH

# Allow natural three-line questions.

QUESTION_MAX_LINES = 3


# ============================================================
# ANCHORS
# ============================================================

ANCHOR_FONT_SIZE = 36

MIN_ANCHOR_FONT_SIZE = 28

ANCHOR_SEPARATOR = "  •  "

# Line 1:
# Anchor 1 • Anchor 2 • Anchor 3
#
# Line 2:
# Anchor 4

ANCHORS_FIRST_LINE = 3

ANCHOR_LINE_SPACING = 10

QUESTION_TO_ANCHORS_GAP = 27


# ============================================================
# EDITORIAL SPACING
# ============================================================

MIN_EDITORIAL_GAP = 55


# ============================================================
# CONTENT RULES
# ============================================================

MAX_EDITORIALS = 4

ANCHORS_PER_EDITORIAL = 4


# ============================================================
# TYPOGRAPHY
# ============================================================

FONT_REGULAR_NAME = "Calibri"

FONT_BOLD_NAME = "Calibri-Bold"

FONT_ITALIC_NAME = "Calibri-Italic"

FONT_BOLD_ITALIC_NAME = "Calibri-BoldItalic"


# ============================================================
# OUTPUT
# ============================================================

SOCIAL_FILENAME_SUFFIX = "_Social"

SOCIAL_FILE_EXTENSION = ".png"


# ============================================================
# QUALITY
# ============================================================

OUTPUT_DPI = 144