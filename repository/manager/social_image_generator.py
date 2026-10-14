
"""Generate a 1080 x 1920 portrait social image from daily INPUT.json."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "input_processing" / "INPUT.json"


# ============================================================
# IMAGE SETTINGS
# ============================================================

W, H = 1080, 1920

BG = "#f8f9fb"
INK = "#17263d"
MUTED = "#4c5b6e"
ACCENT = "#234c75"
DIVIDER = "#dce3eb"


# ============================================================
# FONT SETTINGS
# ============================================================

TITLE_SIZE = 40
BRAND_SIZE = 33
DATE_SIZE = 33

NUMBER_SIZE = 34
QUESTION_SIZE = 39
ANCHOR_SIZE = 32

FOOTER_SIZE = 23


# ============================================================
# SPACING SETTINGS
# ============================================================

QUESTION_LINE_GAP = 20
ANCHOR_LINE_GAP = 12
QUESTION_ANCHOR_GAP = 28


# ============================================================
# FONT LOADER
# ============================================================

def font(size: int, bold: bool = False):

    fonts = ROOT / "assets" / "fonts"

    if bold:
        candidates = [
            fonts / "DejaVuSans-Bold.ttf",
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path(
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans-Bold.ttf"
            ),
        ]
    else:
        candidates = [
            fonts / "DejaVuSans.ttf",
            Path("C:/Windows/Fonts/arial.ttf"),
            Path(
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans.ttf"
            ),
        ]

    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)

    raise FileNotFoundError(
        "Install DejaVu Sans fonts or provide Arial "
        "in Windows Fonts."
    )


# ============================================================
# DATA HELPERS
# ============================================================

def get(obj: dict, *keys, default=None):

    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]

    return default


def wrap(draw, text, fnt, max_width):
    """Wrap text without reducing its font size."""

    words = str(text).split()
    lines = []
    line = ""

    for word in words:

        trial = f"{line} {word}".strip()

        text_width = draw.textbbox(
            (0, 0),
            trial,
            font=fnt
        )[2]

        if text_width <= max_width:
            line = trial

        else:
            if line:
                lines.append(line)

            line = word

    if line:
        lines.append(line)

    return lines


# ============================================================
# EXTRACT EDITORIAL QUESTIONS AND ANCHORS
# ============================================================

def extract(data):

    records = get(
        data,
        "editorials",
        "topics",
        "records"
    )

    if isinstance(records, dict):
        records = list(records.values())

    if not isinstance(records, list):
        raise ValueError(
            "INPUT.json must contain an editorials list."
        )

    output = []

    for index, record in enumerate(records[:4], 1):

        question = get(
            record,
            "question",
            "curiosity_question"
        )

        anchors = get(
            record,
            "anchors",
            "recall_anchors"
        )

        if isinstance(question, dict):
            question = get(
                question,
                "question",
                "text"
            )

        if isinstance(anchors, dict):
            anchors = get(
                anchors,
                "anchors",
                "phrases",
                "items"
            )

        if isinstance(anchors, str):
            anchors = [
                item.strip()
                for item in anchors.split("\n")
                if item.strip()
            ]

        if (
            not question
            or not isinstance(anchors, list)
            or len(anchors) != 4
        ):
            raise ValueError(
                f"Editorial {index}: expected a question "
                "and exactly four anchors."
            )

        anchors = [
            str(
                get(
                    anchor,
                    "text",
                    "phrase",
                    default=""
                )
                if isinstance(anchor, dict)
                else anchor
            ).strip()
            for anchor in anchors
        ]

        if any(not anchor for anchor in anchors):
            raise ValueError(
                f"Editorial {index}: empty recall anchor."
            )

        output.append(
            (
                str(question).strip(),
                anchors
            )
        )

    if not output:
        raise ValueError("No editorials found.")

    return output


# ============================================================
# GENERATE SOCIAL IMAGE
# ============================================================

def generate():

    # LOAD INPUT
    with INPUT.open("r", encoding="utf-8") as file:
        data = json.load(file)

    date = datetime.strptime(
        data["publication_date"],
        "%d %B %Y"
    )

    items = extract(data)

    # OUTPUT PATH
    destination = (
        ROOT
        / "output"
        / str(date.year)
        / f"{date.month:02d}_{date:%B}"
    )

    destination.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        destination
        / f"UAK_Editorials_Social_{date:%y%m%d}.png"
    )

    # CREATE IMAGE
    image = Image.new(
        "RGB",
        (W, H),
        BG
    )

    draw = ImageDraw.Draw(image)

    # 5% TOP AND BOTTOM EMPTY MARGINS
    left = 85
    right = W - 85

    top = int(H * 0.05)
    bottom = int(H * 0.95)

    def centered(text, y, fnt, color):

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=fnt
        )

        text_width = bbox[2] - bbox[0]

        draw.text(
            (
                (W - text_width) / 2,
                y
            ),
            text,
            font=fnt,
            fill=color
        )

    # ========================================================
    # HEADER
    # ========================================================

    # LINE 1: MAIN TITLE
    centered(
        "ONEPAGE STUDY - EDITORIALS DAILY",
        top + 18,
        font(TITLE_SIZE, True),
        INK
    )

    # LINE 2: UPSC ANCHOR WITH KUMAR
    # Same dark navy colour as the main title.
    centered(
        "UPSC Anchor with Kumar",
        top + 79,
        font(BRAND_SIZE, True),
        INK
    )

    # LINE 3: PUBLICATION DATE
    centered(
        date.strftime("%d %B %Y").upper(),
        top + 142,
        font(DATE_SIZE, True),
        ACCENT
    )

    # HEADER DIVIDER
    draw.line(
        (
            left,
            top + 213,
            right,
            top + 213
        ),
        fill="#cdd7e1",
        width=2
    )

    # ========================================================
    # EDITORIAL CONTENT
    # ========================================================

    # Reserve footer space.
    footer_y = bottom - 42
    footer_divider_y = footer_y - 28

    content_start = top + 260
    content_end = footer_divider_y - 35

    block_height = (
        content_end - content_start
    ) / len(items)

    for i, (question, anchors) in enumerate(items):

        block_top = (
            content_start
            + i * block_height
        )

        y = int(block_top + 16)

        x = left + 62
        width = right - x

        # QUESTION FONT
        # Fit question into two lines when possible.
        for qsize in range(
            QUESTION_SIZE,
            23,
            -1
        ):

            qfont = font(
                qsize,
                True
            )

            question_lines = wrap(
                draw,
                question,
                qfont,
                width
            )

            if len(question_lines) <= 2:
                break

        # ANCHORS
        # Fixed 32 px font, automatically wraps.
        afont = font(ANCHOR_SIZE)

        anchor_text = " · ".join(anchors)

        anchor_lines = wrap(
            draw,
            anchor_text,
            afont,
            width
        )

        # SECTION HEIGHT VALIDATION
        question_height = (
            len(question_lines)
            * (
                qsize
                + QUESTION_LINE_GAP
            )
        )

        anchor_height = (
            len(anchor_lines)
            * (
                ANCHOR_SIZE
                + ANCHOR_LINE_GAP
            )
        )

        required_height = (
            question_height
            + QUESTION_ANCHOR_GAP
            + anchor_height
        )

        available_height = (
            block_height - 65
        )

        if required_height > available_height:
            raise ValueError(
                f"Editorial {i + 1}: content exceeds "
                "the available section height."
            )

        # EDITORIAL NUMBER
        draw.text(
            (
                left,
                y
            ),
            f"{i + 1:02d}",
            font=font(
                NUMBER_SIZE,
                True
            ),
            fill=ACCENT
        )

        # QUESTION
        for line in question_lines:

            draw.text(
                (
                    x,
                    y
                ),
                line,
                font=qfont,
                fill=INK
            )

            y += (
                qsize
                + QUESTION_LINE_GAP
            )

        y += QUESTION_ANCHOR_GAP

        # RECALL ANCHORS
        for line in anchor_lines:

            draw.text(
                (
                    x,
                    y
                ),
                line,
                font=afont,
                fill=ACCENT
            )

            y += (
                ANCHOR_SIZE
                + ANCHOR_LINE_GAP
            )

        # DIVIDER BETWEEN EDITORIALS
        if i < len(items) - 1:

            divider_y = int(
                content_start
                + (i + 1) * block_height
                - 20
            )

            draw.line(
                (
                    left,
                    divider_y,
                    right,
                    divider_y
                ),
                fill=DIVIDER,
                width=2
            )

    # ========================================================
    # FOOTER
    # ========================================================

    draw.line(
        (
            left,
            footer_divider_y,
            right,
            footer_divider_y
        ),
        fill="#cdd7e1",
        width=2
    )

    telegram_text = "@upscanchorwithkumar"
    edition_code = f"UAK-ED-{date:%y%m%d}"

    footer_font = font(
        FOOTER_SIZE
    )

    code_font = font(
        FOOTER_SIZE,
        True
    )

    # BOTTOM LEFT: TELEGRAM HANDLE
    draw.text(
        (
            left,
            footer_y
        ),
        telegram_text,
        font=footer_font,
        fill=MUTED
    )

    # BOTTOM RIGHT: UAK CODE
    code_width = draw.textbbox(
        (0, 0),
        edition_code,
        font=code_font
    )[2]

    draw.text(
        (
            right - code_width,
            footer_y
        ),
        edition_code,
        font=code_font,
        fill=ACCENT
    )

    # ========================================================
    # SAVE IMAGE
    # ========================================================

    image.save(
        path,
        "PNG",
        optimize=True
    )

    print()
    print("=" * 72)
    print("SOCIAL IMAGE GENERATED")
    print("=" * 72)
    print(f"Image size   : {W} x {H}")
    print(f"Image path   : {path}")
    print(f"Editorials   : {len(items)}")
    print(f"Anchor font  : {ANCHOR_SIZE} px")
    print(f"Edition code : {edition_code}")
    print("=" * 72)

    return path


if __name__ == "__main__":
    generate()
