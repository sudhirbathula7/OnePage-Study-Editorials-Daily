from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import src.branding as BRAND

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


# ============================================================
# PROJECT
# ============================================================

PROJECT_NAME: Final[str] = BRAND.BRAND_NAME

PUBLICATION_TITLE: Final[str] = BRAND.PUBLICATION_TITLE

PUBLICATION_SUBTITLE: Final[str] = BRAND.PUBLICATION_SUBTITLE

PROJECT_VERSION: Final[str] = "1.0"

DEBUG: Final[bool] = True


# ============================================================
# FILES
# ============================================================

INPUT_FILENAME: Final[str] = "INPUT.json"

OUTPUT_FOLDER: Final[str] = "output"


# ============================================================
# ROOT PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parent.parent
)

INPUT_PATH: Final[Path] = (
    PROJECT_ROOT
    / "input_processing"
    / INPUT_FILENAME
)

OUTPUT_PATH: Final[Path] = (
    PROJECT_ROOT
    / OUTPUT_FOLDER
)


# ============================================================
# PAGE
# ============================================================

PAGE_WIDTH: Final[float] = A4[0]

PAGE_HEIGHT: Final[float] = A4[1]

PAGE_MARGIN_LEFT: Final[float] = 11 * mm

PAGE_MARGIN_RIGHT: Final[float] = 11 * mm

PAGE_MARGIN_TOP: Final[float] = 6 * mm

PAGE_MARGIN_BOTTOM: Final[float] = 6 * mm


CONTENT_WIDTH: Final[float] = (
    PAGE_WIDTH
    - PAGE_MARGIN_LEFT
    - PAGE_MARGIN_RIGHT
)

CONTENT_HEIGHT: Final[float] = (
    PAGE_HEIGHT
    - PAGE_MARGIN_TOP
    - PAGE_MARGIN_BOTTOM
)


# ============================================================
# EDITORIAL STUDY
# ============================================================

# The OnePage Study format is designed around four
# short editorials on one A4 page.
#
# This is a PDF layout target, not an input restriction.
# The input pipeline can still accept fewer editorials.

EDITORIALS_PER_PAGE: Final[int] = 4

POINTS_PER_EDITORIAL: Final[int] = 4

ANCHORS_PER_EDITORIAL: Final[int] = 4


# ============================================================
# PAGE OBJECT
# ============================================================

@dataclass(frozen=True)
class PageDimensions:
    width: float = PAGE_WIDTH
    height: float = PAGE_HEIGHT

    margin_left: float = PAGE_MARGIN_LEFT
    margin_right: float = PAGE_MARGIN_RIGHT
    margin_top: float = PAGE_MARGIN_TOP
    margin_bottom: float = PAGE_MARGIN_BOTTOM

    @property
    def content_width(self) -> float:
        return (
            self.width
            - self.margin_left
            - self.margin_right
        )

    @property
    def content_height(self) -> float:
        return (
            self.height
            - self.margin_top
            - self.margin_bottom
        )


PAGE = PageDimensions()