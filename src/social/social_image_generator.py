from __future__ import annotations

from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)

from src.config import PROJECT_ROOT

from src.social.social_config import (
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    BACKGROUND_COLOR,
    QUESTION_TEXT_COLOR,
    ANCHOR_TEXT_COLOR,
    DATE_TEXT_COLOR,
    BRAND_TEXT_COLOR,
    HEADING_TEXT_COLOR,
    BRAND_FONT_SIZE,
    DATE_FONT_SIZE,
    PRODUCT_HEADING,
    PRODUCT_HEADING_FONT_SIZE,
    QUESTION_FONT_SIZE,
    QUESTION_LINE_SPACING,
    ANCHOR_FONT_SIZE,
    ANCHOR_LINE_SPACING,
    SOCIAL_FILENAME_SUFFIX,
    SOCIAL_FILE_EXTENSION,
)

from src.social.social_data import (
    SocialImageData,
    load_social_image_data,
)

from src.social.social_layout import (
    SocialFonts,
    build_social_layout,
    centered_text_x,
)


# ============================================================
# BRANDING
# ============================================================

BRAND_NAME = (
    "UPSC Anchor with Kumar"
)


# ============================================================
# ASSET PATHS
# ============================================================

BRANDING_DIR = (
    PROJECT_ROOT
    / "assets"
    / "branding"
)

FONTS_DIR = (
    PROJECT_ROOT
    / "assets"
    / "fonts"
)

WINDOWS_FONTS_DIR = Path(
    r"C:\Windows\Fonts"
)


LOGO_CANDIDATES = (
    BRANDING_DIR
    / "brand_logo.png",

    BRANDING_DIR
    / "logo.png",

    PROJECT_ROOT
    / "src"
    / "pdf"
    / "assets"
    / "logos"
    / "brand_logo.png",
)


# ============================================================
# FONT DISCOVERY
# ============================================================

def _find_font(
    candidates: tuple[str, ...],
) -> Path:

    for filename in candidates:

        path = (
            FONTS_DIR
            / filename
        )

        if path.exists():
            return path

    lowered_candidates = {
        filename.lower()
        for filename in candidates
    }

    if FONTS_DIR.exists():

        for path in FONTS_DIR.rglob("*"):

            if (
                path.is_file()
                and path.name.lower()
                in lowered_candidates
            ):
                return path

    for filename in candidates:

        path = (
            WINDOWS_FONTS_DIR
            / filename
        )

        if path.exists():
            return path

    raise FileNotFoundError(
        "Required Calibri font could not be found."
    )


def _get_regular_font_path() -> Path:

    return _find_font(
        (
            "calibri.ttf",
            "Calibri.ttf",
        )
    )


def _get_bold_font_path() -> Path:

    return _find_font(
        (
            "calibrib.ttf",
            "Calibri-Bold.ttf",
            "calibri-bold.ttf",
            "CalibriBold.ttf",
        )
    )


# ============================================================
# LOGO
# ============================================================

def _find_logo() -> Path:

    for path in LOGO_CANDIDATES:

        if path.exists():
            return path

    raise FileNotFoundError(
        "Brand logo could not be found."
    )


def _load_logo(
    logo_path: Path,
    width: int,
    height: int,
) -> Image.Image:

    logo = Image.open(
        logo_path
    ).convert("RGBA")

    logo.thumbnail(
        (
            width,
            height,
        ),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        (
            255,
            255,
            255,
            0,
        ),
    )

    x = int(
        (
            width
            - logo.width
        )
        / 2
    )

    y = int(
        (
            height
            - logo.height
        )
        / 2
    )

    canvas.alpha_composite(
        logo,
        (
            x,
            y,
        ),
    )

    return canvas


# ============================================================
# FONTS
# ============================================================

def _load_fonts(
    regular_font_path: Path,
    bold_font_path: Path,
) -> SocialFonts:

    return SocialFonts(

        brand=ImageFont.truetype(
            str(bold_font_path),
            BRAND_FONT_SIZE,
        ),

        date=ImageFont.truetype(
            str(regular_font_path),
            DATE_FONT_SIZE,
        ),

        product_heading=ImageFont.truetype(
            str(bold_font_path),
            PRODUCT_HEADING_FONT_SIZE,
        ),

        question=ImageFont.truetype(
            str(bold_font_path),
            QUESTION_FONT_SIZE,
        ),

        anchor=ImageFont.truetype(
            str(regular_font_path),
            ANCHOR_FONT_SIZE,
        ),
    )


# ============================================================
# QUESTION DRAWING
# ============================================================

def _draw_centered_question(
    draw: ImageDraw.ImageDraw,
    *,
    lines: tuple[str, ...],
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:

    current_y = y

    for line in lines:

        x = centered_text_x(
            draw,
            line,
            font,
        )

        draw.text(
            (
                x,
                current_y,
            ),
            line,
            font=font,
            fill=QUESTION_TEXT_COLOR,
        )

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font,
        )

        line_height = (
            bbox[3]
            - bbox[1]
        )

        current_y += (
            line_height
            + QUESTION_LINE_SPACING
        )


# ============================================================
# ANCHOR DRAWING
# ============================================================

def _draw_centered_anchors(
    draw: ImageDraw.ImageDraw,
    *,
    lines: tuple[str, ...],
    y: int,
    font: ImageFont.FreeTypeFont,
) -> None:

    current_y = y

    for line in lines:

        x = centered_text_x(
            draw,
            line,
            font,
        )

        draw.text(
            (
                x,
                current_y,
            ),
            line,
            font=font,
            fill=ANCHOR_TEXT_COLOR,
        )

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font,
        )

        line_height = (
            bbox[3]
            - bbox[1]
        )

        current_y += (
            line_height
            + ANCHOR_LINE_SPACING
        )


# ============================================================
# OUTPUT FILENAME
# ============================================================

def _build_social_filename(
    publication_date_iso: str,
) -> str:

    compact_date = (
        publication_date_iso[2:]
        .replace(
            "-",
            "",
        )
    )

    return (
        "UAK_Editorials_Daily_"
        f"{compact_date}"
        f"{SOCIAL_FILENAME_SUFFIX}"
        f"{SOCIAL_FILE_EXTENSION}"
    )


# ============================================================
# GENERATOR
# ============================================================

def generate_social_image(
    data: SocialImageData | None = None,
    output_path: Path | str | None = None,
) -> Path:

    if data is None:
        data = (
            load_social_image_data()
        )

    regular_font_path = (
        _get_regular_font_path()
    )

    bold_font_path = (
        _get_bold_font_path()
    )

    logo_path = (
        _find_logo()
    )

    fonts = _load_fonts(
        regular_font_path,
        bold_font_path,
    )

    image = Image.new(
        "RGB",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT,
        ),
        BACKGROUND_COLOR,
    )

    draw = ImageDraw.Draw(
        image
    )

    questions = tuple(
        editorial.question
        for editorial
        in data.editorials
    )

    anchors = tuple(
        editorial.anchors
        for editorial
        in data.editorials
    )

    layout = build_social_layout(
        draw,
        display_date=(
            data.display_date
        ),
        questions=questions,
        anchors=anchors,
        fonts=fonts,
        anchor_font_path=str(
            regular_font_path
        ),
    )

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    logo = _load_logo(
        logo_path,
        layout.logo_width,
        layout.logo_height,
    )

    image.paste(
        logo,
        (
            layout.logo_x,
            layout.logo_y,
        ),
        logo,
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    draw.text(
        (
            layout.brand_x,
            layout.brand_y,
        ),
        BRAND_NAME,
        font=fonts.brand,
        fill=BRAND_TEXT_COLOR,
    )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    draw.text(
        (
            layout.date_x,
            layout.date_y,
        ),
        data.display_date,
        font=fonts.date,
        fill=DATE_TEXT_COLOR,
    )

    # --------------------------------------------------------
    # PRODUCT HEADING
    # --------------------------------------------------------

    draw.text(
        (
            layout.product_heading_x,
            layout.product_heading_y,
        ),
        PRODUCT_HEADING,
        font=fonts.product_heading,
        fill=HEADING_TEXT_COLOR,
    )

    # --------------------------------------------------------
    # QUESTIONS + ANCHORS
    # --------------------------------------------------------

    for editorial in (
        layout.editorials
    ):

        _draw_centered_question(
            draw,
            lines=(
                editorial.question_lines
            ),
            y=(
                editorial.question_y
            ),
            font=fonts.question,
        )

        _draw_centered_anchors(
            draw,
            lines=(
                editorial.anchor_lines
            ),
            y=(
                editorial.anchor_y
            ),
            font=(
                editorial.anchor_font
            ),
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    if output_path is None:

        output_dir = (
            PROJECT_ROOT
            / "output"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            _build_social_filename(
                data.publication_date_iso
            )
        )

        output_path = (
            output_dir
            / filename
        )

    else:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path


# ============================================================
# TEST
# ============================================================

def main() -> None:

    output_path = (
        generate_social_image()
    )

    print()

    print(
        "SOCIAL IMAGE GENERATED"
    )

    print(
        "=" * 60
    )

    print(
        f"File: {output_path}"
    )

    print(
        f"Size: "
        f"{IMAGE_WIDTH} × "
        f"{IMAGE_HEIGHT}"
    )

    print()


if __name__ == "__main__":
    main()