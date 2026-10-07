import json
import re
import sys

from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "INPUT.json"
)

INPUT_CANDIDATES = (
    PROJECT_ROOT / "INPUT_DATA.txt",
    PROJECT_ROOT / "input.txt",
    PROJECT_ROOT / "INPUT.txt",
)


# ============================================================
# CONSTANTS
# ============================================================

PUBLICATION_DATE_HEADING = "PUBLICATION DATE"

SUPPORTED_PUBLICATION_DATE_FORMATS = (
    "%d.%m.%y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d %B %Y",
    "%d %b %Y",
)

EDITORIAL_SECTION_HEADINGS = (
    "HEADING",
    "GS PAPER",
    "QUESTION",
    "POINT 1",
    "POINT 2",
    "POINT 3",
    "POINT 4",
    "TAKEAWAY",
    "ANCHORS",
)

VALID_GS_PAPERS = {
    "GS I",
    "GS II",
    "GS III",
    "GS IV",
}


# ============================================================
# ERRORS
# ============================================================

class ConversionError(ValueError):
    """Raised when INPUT_DATA.txt cannot be converted safely."""


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean(value: str) -> str:
    """
    Normalize line endings and unnecessary whitespace while
    preserving meaningful paragraph structure.
    """

    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")

    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )

    value = re.sub(
        r"\n[ \t]+",
        "\n",
        value,
    )

    return value.strip()


def _nonempty_lines(value: str) -> list[str]:
    """Return only non-empty stripped lines."""

    return [
        line.strip()
        for line in value.splitlines()
        if line.strip()
    ]


def _find_input_file() -> Path:
    """Find the project's text input file."""

    for path in INPUT_CANDIDATES:
        if path.exists():
            return path

    expected = ", ".join(
        path.name
        for path in INPUT_CANDIDATES
    )

    raise FileNotFoundError(
        "No input text file was found in the project root.\n"
        f"Expected one of: {expected}"
    )


# ============================================================
# PUBLICATION DATE
# ============================================================

def _parse_publication_date(
    raw_date: str,
) -> datetime:

    cleaned_date = _clean(raw_date)

    for date_format in SUPPORTED_PUBLICATION_DATE_FORMATS:
        try:
            return datetime.strptime(
                cleaned_date,
                date_format,
            )

        except ValueError:
            continue

    raise ConversionError(
        "Unsupported PUBLICATION DATE format.\n\n"
        "Examples:\n"
        "21.09.2026\n"
        "21-09-2026\n"
        "21/09/2026\n"
        "21 September 2026"
    )


def _extract_publication_date(
    text: str,
) -> tuple[str, str]:

    normalized = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    first_editorial = re.search(
        r"(?mi)^\s*EDITORIAL\s+\d+\s*$",
        normalized,
    )

    if not first_editorial:
        raise ConversionError(
            "No 'EDITORIAL X' heading was found."
        )

    metadata = normalized[
        :first_editorial.start()
    ]

    date_match = re.search(
        rf"(?mi)"
        rf"^\s*{re.escape(PUBLICATION_DATE_HEADING)}\s*$"
        rf"\s*"
        rf"^\s*(.+?)\s*$",
        metadata,
    )

    if not date_match:
        raise ConversionError(
            "Missing PUBLICATION DATE at the top "
            "of INPUT_DATA.txt."
        )

    parsed_date = _parse_publication_date(
        date_match.group(1)
    )

    display_date = parsed_date.strftime(
        "%d %B %Y"
    )

    iso_date = parsed_date.strftime(
        "%Y-%m-%d"
    )

    return display_date, iso_date


# ============================================================
# EDITORIAL SPLITTING
# ============================================================

def _split_editorials(
    text: str,
) -> list[tuple[int, str]]:

    normalized = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    matches = list(
        re.finditer(
            r"(?mi)^\s*EDITORIAL\s+(\d+)\s*$",
            normalized,
        )
    )

    if not matches:
        raise ConversionError(
            "No 'EDITORIAL X' headings were found."
        )

    editorials: list[
        tuple[int, str]
    ] = []

    for index, match in enumerate(matches):

        editorial_number = int(
            match.group(1)
        )

        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(normalized)
        )

        block = normalized[
            start:end
        ].strip()

        editorials.append(
            (
                editorial_number,
                block,
            )
        )

    return editorials


# ============================================================
# SECTION EXTRACTION
# ============================================================

def _extract_sections(
    block: str,
    editorial_number: int,
) -> dict[str, str]:

    headings_pattern = "|".join(
        re.escape(heading)
        for heading in EDITORIAL_SECTION_HEADINGS
    )

    pattern = re.compile(
        rf"(?mi)^\s*({headings_pattern})\s*$"
    )

    matches = list(
        pattern.finditer(block)
    )

    found_headings = [
        match.group(1).upper()
        for match in matches
    ]

    missing = [
        heading
        for heading in EDITORIAL_SECTION_HEADINGS
        if heading not in found_headings
    ]

    duplicates = sorted(
        {
            heading
            for heading in found_headings
            if found_headings.count(heading) > 1
        }
    )

    if missing:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "missing section(s): "
            + ", ".join(missing)
        )

    if duplicates:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "duplicate section(s): "
            + ", ".join(duplicates)
        )

    sections: dict[str, str] = {}

    for index, match in enumerate(matches):

        heading = match.group(1).upper()

        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(block)
        )

        sections[heading] = _clean(
            block[start:end]
        )

    return sections


# ============================================================
# GS PAPER
# ============================================================

def _normalize_gs_paper(
    value: str,
    editorial_number: int,
) -> str:

    value = _clean(value).upper()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    # Allow:
    # GS I
    # GS II
    # GS III
    # GS IV
    #
    # Also tolerate:
    # GS 1
    # GS 2
    # GS 3
    # GS 4

    numeric_map = {
        "GS 1": "GS I",
        "GS 2": "GS II",
        "GS 3": "GS III",
        "GS 4": "GS IV",
    }

    value = numeric_map.get(
        value,
        value,
    )

    if value not in VALID_GS_PAPERS:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "GS PAPER must be one of: "
            "GS I, GS II, GS III, GS IV."
        )

    return value


# ============================================================
# ANCHORS
# ============================================================

def _parse_anchors(
    value: str,
    editorial_number: int,
) -> list[str]:

    anchors = _nonempty_lines(value)

    # Also tolerate:
    # 1. anchor
    # 2. anchor
    # etc.

    anchors = [
        re.sub(
            r"^\d+\.\s*",
            "",
            anchor,
        ).strip()
        for anchor in anchors
    ]

    if len(anchors) != 4:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "ANCHORS must contain exactly 4 "
            "non-empty lines — one anchor for "
            "each of Points 1–4."
        )

    if any(
        not anchor
        for anchor in anchors
    ):
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "anchors cannot be empty."
        )

    return anchors


def _anchor_exists_in_point(
    anchor: str,
    point: str,
) -> bool:
    """
    Check whether the manually selected anchor exists
    inside its corresponding point.

    Matching is case-insensitive so:
        Sanctions
    can match:
        sanctions
    """

    return (
        anchor.casefold()
        in point.casefold()
    )


# ============================================================
# EDITORIAL PARSER
# ============================================================

def _parse_editorial(
    editorial_number: int,
    block: str,
) -> dict[str, Any]:

    sections = _extract_sections(
        block,
        editorial_number,
    )

    heading = _clean(
        sections["HEADING"]
    )

    gs_paper = _normalize_gs_paper(
        sections["GS PAPER"],
        editorial_number,
    )

    question = _clean(
        sections["QUESTION"]
    )

    takeaway = _clean(
        sections["TAKEAWAY"]
    )

    points = [
        _clean(
            sections[f"POINT {number}"]
        )
        for number in range(1, 5)
    ]

    anchors = _parse_anchors(
        sections["ANCHORS"],
        editorial_number,
    )

    # --------------------------------------------------------
    # REQUIRED CONTENT
    # --------------------------------------------------------

    if not heading:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "HEADING cannot be empty."
        )

    if not question:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "QUESTION cannot be empty."
        )

    for number, point in enumerate(
        points,
        start=1,
    ):
        if not point:
            raise ConversionError(
                f"EDITORIAL {editorial_number}: "
                f"POINT {number} cannot be empty."
            )

    if not takeaway:
        raise ConversionError(
            f"EDITORIAL {editorial_number}: "
            "TAKEAWAY cannot be empty."
        )

    # --------------------------------------------------------
    # ANCHOR ↔ POINT VALIDATION
    # --------------------------------------------------------

    for number, (
        point,
        anchor,
    ) in enumerate(
        zip(points, anchors),
        start=1,
    ):

        if not _anchor_exists_in_point(
            anchor,
            point,
        ):
            raise ConversionError(
                f"EDITORIAL {editorial_number}: "
                f"ANCHOR {number} ('{anchor}') "
                f"was not found inside POINT {number}.\n"
                "Each anchor must be copied directly "
                "from its corresponding point."
            )

    # --------------------------------------------------------
    # FINAL POINT STRUCTURE
    # --------------------------------------------------------

    point_data = [
        {
            "number": number,
            "text": point,
            "anchor": anchor,
        }
        for number, (
            point,
            anchor,
        ) in enumerate(
            zip(points, anchors),
            start=1,
        )
    ]

    return {
        "editorial_number": editorial_number,
        "heading": heading,
        "gs_paper": gs_paper,

        # Stored for revision / future social use.
        # Not intended for the main PDF.
        "question": question,

        # Main PDF content.
        "points": point_data,
        "takeaway": takeaway,

        # Also stored separately for convenient
        # revision-data access.
        "anchors": anchors,
    }


# ============================================================
# COMPLETE CONVERSION
# ============================================================

def convert_text(
    text: str,
) -> dict[str, Any]:

    (
        publication_date,
        publication_date_iso,
    ) = _extract_publication_date(text)

    editorial_blocks = _split_editorials(
        text
    )

    # Editorial numbering must be sequential.
    numbers = [
        number
        for number, _ in editorial_blocks
    ]

    expected_numbers = list(
        range(
            1,
            len(numbers) + 1,
        )
    )

    if numbers != expected_numbers:
        raise ConversionError(
            "EDITORIAL numbering must start at 1 "
            "and continue sequentially.\n"
            f"Found: {numbers}\n"
            f"Expected: {expected_numbers}"
        )

    editorials = [
        _parse_editorial(
            editorial_number,
            block,
        )
        for editorial_number, block
        in editorial_blocks
    ]

    if not editorials:
         raise ConversionError(
        "INPUT_DATA.txt must contain at least "
        "one completed editorial."
    )

    return {
        "schema_version": "1.0",
        "publication_date": publication_date,
        "publication_date_iso": (
            publication_date_iso
        ),
        "editorial_count": len(editorials),
        "editorials": editorials,
    }


# ============================================================
# FILE CONVERSION
# ============================================================

def convert_file(
    input_path: Path,
    output_path: Path = OUTPUT_PATH,
) -> Path:

    text = input_path.read_text(
        encoding="utf-8-sig"
    )

    data = convert_text(text)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = (
        output_path.with_suffix(
            ".json.tmp"
        )
    )

    temporary_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(
        output_path
    )

    return output_path


# ============================================================
# COMMAND LINE
# ============================================================

def main() -> int:

    try:
        input_path = _find_input_file()

        output_path = convert_file(
            input_path
        )

        data = json.loads(
            output_path.read_text(
                encoding="utf-8"
            )
        )

        print()
        print("CONVERSION SUCCESSFUL")
        print("---------------------")
        print(
            f"Input:      {input_path}"
        )
        print(
            f"Created:    {output_path}"
        )
        print(
            "Date:       "
            f"{data['publication_date']}"
        )
        print(
            "Editorials: "
            f"{data['editorial_count']}"
        )
        print()

        for editorial in data["editorials"]:
            print(
                f"{editorial['editorial_number']}. "
                f"{editorial['heading']} "
                f"({editorial['gs_paper']})"
            )

        print()

        return 0

    except (
        OSError,
        ConversionError,
    ) as exc:

        print()
        print(
            "CONVERSION FAILED"
        )
        print(
            "-----------------"
        )
        print(
            str(exc),
            file=sys.stderr,
        )
        print()

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )