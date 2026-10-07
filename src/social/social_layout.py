from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PIL import ImageDraw, ImageFont

from src.social.social_config import (
    IMAGE_WIDTH,
    RIGHT_MARGIN,
    CONTENT_WIDTH,
    USABLE_BOTTOM,
    LOGO_WIDTH,
    LOGO_HEIGHT,
    LOGO_X,
    LOGO_Y,
    LOGO_BRAND_GAP,
    PRODUCT_HEADING,
    TOP_ROW_TO_HEADING_GAP,
    HEADING_TO_CONTENT_GAP,
    QUESTION_LINE_SPACING,
    QUESTION_MAX_WIDTH,
    QUESTION_MAX_LINES,
    ANCHOR_FONT_SIZE,
    MIN_ANCHOR_FONT_SIZE,
    ANCHOR_SEPARATOR,
    ANCHORS_FIRST_LINE,
    ANCHOR_LINE_SPACING,
    QUESTION_TO_ANCHORS_GAP,
    MIN_EDITORIAL_GAP,
    MAX_EDITORIALS,
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass(frozen=True)
class SocialFonts:
    brand: ImageFont.FreeTypeFont
    date: ImageFont.FreeTypeFont
    product_heading: ImageFont.FreeTypeFont
    question: ImageFont.FreeTypeFont
    anchor: ImageFont.FreeTypeFont


@dataclass(frozen=True)
class EditorialLayout:
    question_lines: tuple[str, ...]

    question_y: int
    question_height: int

    anchor_lines: tuple[str, ...]
    anchor_font: ImageFont.FreeTypeFont

    anchor_y: int
    anchor_height: int


@dataclass(frozen=True)
class SocialLayout:
    logo_x: int
    logo_y: int
    logo_width: int
    logo_height: int

    brand_x: int
    brand_y: int

    date_x: int
    date_y: int

    product_heading_x: int
    product_heading_y: int

    editorials: tuple[EditorialLayout, ...]


# ============================================================
# TEXT MEASUREMENT
# ============================================================

def _text_bbox(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int, int, int]:

    return draw.textbbox(
        (0, 0),
        text,
        font=font,
    )


def text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> int:

    bbox = _text_bbox(
        draw,
        text,
        font,
    )

    return bbox[2] - bbox[0]


def text_height(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> int:

    bbox = _text_bbox(
        draw,
        text,
        font,
    )

    return bbox[3] - bbox[1]


# ============================================================
# QUESTION WRAPPING
# ============================================================

def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> tuple[str, ...]:

    words = text.split()

    if not words:
        return ("",)

    lines: list[str] = []
    current_line = words[0]

    for word in words[1:]:

        candidate = (
            f"{current_line} {word}"
        )

        if (
            text_width(
                draw,
                candidate,
                font,
            )
            <= max_width
        ):
            current_line = candidate

        else:
            lines.append(
                current_line
            )

            current_line = word

    lines.append(
        current_line
    )

    return tuple(lines)


def question_block_height(
    draw: ImageDraw.ImageDraw,
    lines: Sequence[str],
    font: ImageFont.FreeTypeFont,
) -> int:

    if not lines:
        return 0

    heights = [
        text_height(
            draw,
            line,
            font,
        )
        for line in lines
    ]

    return (
        sum(heights)
        + QUESTION_LINE_SPACING
        * (len(lines) - 1)
    )


# ============================================================
# CENTERING
# ============================================================

def centered_text_x(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> int:

    width = text_width(
        draw,
        text,
        font,
    )

    return int(
        (
            IMAGE_WIDTH
            - width
        )
        / 2
    )


def question_line_x(
    draw: ImageDraw.ImageDraw,
    line: str,
    font: ImageFont.FreeTypeFont,
) -> int:

    return centered_text_x(
        draw,
        line,
        font,
    )


# ============================================================
# ANCHOR LINES
# ============================================================

def build_anchor_lines(
    anchors: Sequence[str],
) -> tuple[str, ...]:
    """
    Format four anchors as:

    Anchor 1 • Anchor 2 • Anchor 3
    Anchor 4
    """

    clean_anchors = tuple(
        anchor.strip()
        for anchor in anchors
        if anchor.strip()
    )

    if not clean_anchors:
        return tuple()

    first_line = ANCHOR_SEPARATOR.join(
        clean_anchors[
            :ANCHORS_FIRST_LINE
        ]
    )

    remaining = clean_anchors[
        ANCHORS_FIRST_LINE:
    ]

    if not remaining:
        return (
            first_line,
        )

    second_line = ANCHOR_SEPARATOR.join(
        remaining
    )

    return (
        first_line,
        second_line,
    )


def fit_anchor_font(
    draw: ImageDraw.ImageDraw,
    anchor_lines: Sequence[str],
    font_path: str,
) -> ImageFont.FreeTypeFont:
    """
    Fit the longest anchor line inside the content width.
    """

    size = ANCHOR_FONT_SIZE

    while size >= MIN_ANCHOR_FONT_SIZE:

        font = ImageFont.truetype(
            font_path,
            size,
        )

        fits = all(
            text_width(
                draw,
                line,
                font,
            )
            <= CONTENT_WIDTH
            for line in anchor_lines
        )

        if fits:
            return font

        size -= 1

    return ImageFont.truetype(
        font_path,
        MIN_ANCHOR_FONT_SIZE,
    )


def anchor_block_height(
    draw: ImageDraw.ImageDraw,
    anchor_lines: Sequence[str],
    font: ImageFont.FreeTypeFont,
) -> int:

    if not anchor_lines:
        return 0

    heights = [
        text_height(
            draw,
            line,
            font,
        )
        for line in anchor_lines
    ]

    return (
        sum(heights)
        + ANCHOR_LINE_SPACING
        * (len(anchor_lines) - 1)
    )


# ============================================================
# TOP BRAND ROW
# ============================================================

def calculate_brand_y(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
) -> int:

    height = text_height(
        draw,
        "UPSC Anchor with Kumar",
        font,
    )

    return int(
        LOGO_Y
        + (
            LOGO_HEIGHT
            - height
        )
        / 2
    )


def calculate_date_position(
    draw: ImageDraw.ImageDraw,
    display_date: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int]:

    width = text_width(
        draw,
        display_date,
        font,
    )

    height = text_height(
        draw,
        display_date,
        font,
    )

    x = (
        IMAGE_WIDTH
        - RIGHT_MARGIN
        - width
    )

    y = int(
        LOGO_Y
        + (
            LOGO_HEIGHT
            - height
        )
        / 2
    )

    return x, y


# ============================================================
# PRODUCT HEADING
# ============================================================

def calculate_product_heading_position(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int]:

    width = text_width(
        draw,
        PRODUCT_HEADING,
        font,
    )

    x = int(
        (
            IMAGE_WIDTH
            - width
        )
        / 2
    )

    y = (
        LOGO_Y
        + LOGO_HEIGHT
        + TOP_ROW_TO_HEADING_GAP
    )

    return x, y


# ============================================================
# MAIN LAYOUT
# ============================================================

def build_social_layout(
    draw: ImageDraw.ImageDraw,
    *,
    display_date: str,
    questions: Sequence[str],
    anchors: Sequence[Sequence[str]],
    fonts: SocialFonts,
    anchor_font_path: str,
) -> SocialLayout:

    if len(questions) != len(anchors):
        raise ValueError(
            "Questions and anchors must contain "
            "the same number of records."
        )

    if not questions:
        raise ValueError(
            "At least one editorial is required."
        )

    if len(questions) > MAX_EDITORIALS:
        raise ValueError(
            f"A maximum of {MAX_EDITORIALS} "
            f"editorials is supported."
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    brand_x = (
        LOGO_X
        + LOGO_WIDTH
        + LOGO_BRAND_GAP
    )

    brand_y = calculate_brand_y(
        draw,
        fonts.brand,
    )

    date_x, date_y = (
        calculate_date_position(
            draw,
            display_date,
            fonts.date,
        )
    )

    # --------------------------------------------------------
    # PRODUCT HEADING
    # --------------------------------------------------------

    heading_x, heading_y = (
        calculate_product_heading_position(
            draw,
            fonts.product_heading,
        )
    )

    heading_height = text_height(
        draw,
        PRODUCT_HEADING,
        fonts.product_heading,
    )

    editorial_area_top = (
        heading_y
        + heading_height
        + HEADING_TO_CONTENT_GAP
    )

    available_height = (
        USABLE_BOTTOM
        - editorial_area_top
    )

    # --------------------------------------------------------
    # MEASURE GROUPS
    # --------------------------------------------------------

    groups: list[dict] = []

    total_content_height = 0

    for index, question in enumerate(
        questions
    ):

        clean_question = (
            question.strip()
        )

        if not clean_question:
            raise ValueError(
                f"Question {index + 1} is empty."
            )

        question_lines = wrap_text(
            draw,
            clean_question,
            fonts.question,
            QUESTION_MAX_WIDTH,
        )

        if (
            len(question_lines)
            > QUESTION_MAX_LINES
        ):
            raise ValueError(
                f"Question {index + 1} requires "
                f"{len(question_lines)} lines. "
                f"Maximum supported is "
                f"{QUESTION_MAX_LINES}."
            )

        question_height = (
            question_block_height(
                draw,
                question_lines,
                fonts.question,
            )
        )

        anchor_lines = (
            build_anchor_lines(
                anchors[index]
            )
        )

        if not anchor_lines:
            raise ValueError(
                f"Editorial {index + 1} "
                f"contains no anchors."
            )

        anchor_font = (
            fit_anchor_font(
                draw,
                anchor_lines,
                anchor_font_path,
            )
        )

        anchor_height = (
            anchor_block_height(
                draw,
                anchor_lines,
                anchor_font,
            )
        )

        group_height = (
            question_height
            + QUESTION_TO_ANCHORS_GAP
            + anchor_height
        )

        total_content_height += (
            group_height
        )

        groups.append(
            {
                "question_lines": (
                    question_lines
                ),
                "question_height": (
                    question_height
                ),
                "anchor_lines": (
                    anchor_lines
                ),
                "anchor_font": (
                    anchor_font
                ),
                "anchor_height": (
                    anchor_height
                ),
                "group_height": (
                    group_height
                ),
            }
        )

    # --------------------------------------------------------
    # DISTRIBUTE GROUPS
    # --------------------------------------------------------

    gap_count = max(
        len(groups) - 1,
        0,
    )

    if gap_count:

        free_space = (
            available_height
            - total_content_height
        )

        editorial_gap = max(
            MIN_EDITORIAL_GAP,
            int(
                free_space
                / (
                    gap_count
                    + 2
                )
            ),
        )

    else:
        editorial_gap = 0

    total_block_height = (
        total_content_height
        + editorial_gap
        * gap_count
    )

    if (
        total_block_height
        > available_height
    ):
        raise ValueError(
            "Social content does not fit "
            "inside the usable 9:16 area."
        )

    # Center complete editorial block.

    extra_space = (
        available_height
        - total_block_height
    )

    current_y = (
        editorial_area_top
        + int(
            extra_space
            / 2
        )
    )

    # --------------------------------------------------------
    # FINAL POSITIONS
    # --------------------------------------------------------

    editorial_layouts: list[
        EditorialLayout
    ] = []

    for group in groups:

        question_y = current_y

        anchor_y = (
            question_y
            + group["question_height"]
            + QUESTION_TO_ANCHORS_GAP
        )

        editorial_layouts.append(
            EditorialLayout(
                question_lines=(
                    group[
                        "question_lines"
                    ]
                ),
                question_y=(
                    question_y
                ),
                question_height=(
                    group[
                        "question_height"
                    ]
                ),
                anchor_lines=(
                    group[
                        "anchor_lines"
                    ]
                ),
                anchor_font=(
                    group[
                        "anchor_font"
                    ]
                ),
                anchor_y=(
                    anchor_y
                ),
                anchor_height=(
                    group[
                        "anchor_height"
                    ]
                ),
            )
        )

        current_y += (
            group["group_height"]
            + editorial_gap
        )

    # --------------------------------------------------------
    # BOTTOM SAFETY CHECK
    # --------------------------------------------------------

    last = editorial_layouts[-1]

    final_bottom = (
        last.anchor_y
        + last.anchor_height
    )

    if final_bottom > USABLE_BOTTOM:
        raise ValueError(
            "Content entered the reserved "
            "bottom 10% area."
        )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return SocialLayout(
        logo_x=LOGO_X,
        logo_y=LOGO_Y,
        logo_width=LOGO_WIDTH,
        logo_height=LOGO_HEIGHT,
        brand_x=brand_x,
        brand_y=brand_y,
        date_x=date_x,
        date_y=date_y,
        product_heading_x=heading_x,
        product_heading_y=heading_y,
        editorials=tuple(
            editorial_layouts
        ),
    )