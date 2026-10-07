from __future__ import annotations

import json

from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_JSON = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)


# ============================================================
# ERROR
# ============================================================

class KnowledgeLoadError(ValueError):
    """
    Raised when editorial data cannot be loaded safely.
    """


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class EditorialPointRecord:
    """
    One explanatory point inside an editorial.

    The anchor is manually selected from the point text
    and will later be used for bold highlighting in the PDF.
    """

    number: int
    text: str
    anchor: str


@dataclass(frozen=True)
class EditorialRecord:
    """
    One complete short editorial study block.
    """

    editorial_number: int

    heading: str

    gs_paper: str

    question: str

    points: tuple[
        EditorialPointRecord,
        EditorialPointRecord,
        EditorialPointRecord,
        EditorialPointRecord,
    ]

    takeaway: str

    anchors: tuple[
        str,
        str,
        str,
        str,
    ]


@dataclass(frozen=True)
class EditorialStudyData:
    """
    Complete daily editorial study data.

    The number of editorials is intentionally flexible.
    A day may contain 1, 2, 3, 4 or more editorials.

    PDF layout decisions are handled later by the
    rendering layer, not by this loader.
    """

    publication_date: str

    publication_date_iso: str

    editorials: tuple[
        EditorialRecord,
        ...
    ]


# ============================================================
# BASIC HELPERS
# ============================================================

def _required(
    mapping: dict[str, Any],
    key: str,
    context: str,
) -> Any:
    """
    Return a required value.

    This checks structure only.
    It does not apply word-count or writing restrictions.
    """

    if key not in mapping:

        raise KnowledgeLoadError(
            f"{context}: "
            f"missing required field '{key}'."
        )

    return mapping[key]


def _required_text(
    mapping: dict[str, Any],
    key: str,
    context: str,
) -> str:
    """
    Load required text without changing its wording.
    """

    value = _required(
        mapping,
        key,
        context,
    )

    if not isinstance(
        value,
        str,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            f"'{key}' must be text."
        )

    value = value.strip()

    if not value:
        raise KnowledgeLoadError(
            f"{context}: "
            f"'{key}' cannot be empty."
        )

    return value


# ============================================================
# POINT LOADER
# ============================================================

def _load_point(
    raw: Any,
    editorial_number: int,
    position: int,
) -> EditorialPointRecord:

    context = (
        f"Editorial {editorial_number}, "
        f"Point {position}"
    )

    if not isinstance(
        raw,
        dict,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "point must be an object."
        )

    number = _required(
        raw,
        "number",
        context,
    )

    if not isinstance(
        number,
        int,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "'number' must be an integer."
        )

    text = _required_text(
        raw,
        "text",
        context,
    )

    anchor = _required_text(
        raw,
        "anchor",
        context,
    )

    return EditorialPointRecord(
        number=number,
        text=text,
        anchor=anchor,
    )


# ============================================================
# EDITORIAL LOADER
# ============================================================

def _load_editorial(
    raw: Any,
    position: int,
) -> EditorialRecord:

    context = f"Editorial {position}"

    if not isinstance(
        raw,
        dict,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "editorial must be an object."
        )

    # --------------------------------------------------------
    # EDITORIAL NUMBER
    # --------------------------------------------------------

    editorial_number = _required(
        raw,
        "editorial_number",
        context,
    )

    if not isinstance(
        editorial_number,
        int,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "'editorial_number' must be an integer."
        )

    # --------------------------------------------------------
    # BASIC CONTENT
    # --------------------------------------------------------

    heading = _required_text(
        raw,
        "heading",
        context,
    )

    gs_paper = _required_text(
        raw,
        "gs_paper",
        context,
    )

    question = _required_text(
        raw,
        "question",
        context,
    )

    takeaway = _required_text(
        raw,
        "takeaway",
        context,
    )

    # --------------------------------------------------------
    # POINTS
    # --------------------------------------------------------

    points_raw = _required(
        raw,
        "points",
        context,
    )

    if not isinstance(
        points_raw,
        list,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "'points' must be a list."
        )

    if len(points_raw) != 4:
        raise KnowledgeLoadError(
            f"{context}: "
            "exactly 4 points are required. "
            f"Found {len(points_raw)}."
        )

    points = tuple(
        _load_point(
            point,
            editorial_number,
            point_position,
        )
        for point_position, point in enumerate(
            points_raw,
            start=1,
        )
    )

    # --------------------------------------------------------
    # ANCHORS
    # --------------------------------------------------------

    anchors_raw = _required(
        raw,
        "anchors",
        context,
    )

    if not isinstance(
        anchors_raw,
        list,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "'anchors' must be a list."
        )

    if len(anchors_raw) != 4:
        raise KnowledgeLoadError(
            f"{context}: "
            "exactly 4 anchors are required. "
            f"Found {len(anchors_raw)}."
        )

    anchors: list[str] = []

    for anchor_position, anchor in enumerate(
        anchors_raw,
        start=1,
    ):

        if not isinstance(
            anchor,
            str,
        ):
            raise KnowledgeLoadError(
                f"{context}, "
                f"Anchor {anchor_position}: "
                "must be text."
            )

        anchor = anchor.strip()

        if not anchor:
            raise KnowledgeLoadError(
                f"{context}, "
                f"Anchor {anchor_position}: "
                "cannot be empty."
            )

        anchors.append(
            anchor
        )

    # --------------------------------------------------------
    # FINAL RECORD
    # --------------------------------------------------------

    return EditorialRecord(
        editorial_number=editorial_number,
        heading=heading,
        gs_paper=gs_paper,
        question=question,
        points=(
            points[0],
            points[1],
            points[2],
            points[3],
        ),
        takeaway=takeaway,
        anchors=(
            anchors[0],
            anchors[1],
            anchors[2],
            anchors[3],
        ),
    )


# ============================================================
# PUBLIC LOADER
# ============================================================

def load_editorial_study_data(
    input_path: Path = INPUT_JSON,
) -> EditorialStudyData:
    """
    Load the complete daily editorial study file.

    This loader intentionally does not impose:

    - word limits
    - sentence limits
    - heading word counts
    - question word counts
    - point word counts
    - takeaway word counts
    - anchor word counts

    Those are content-generation considerations,
    not data-loading rules.
    """

    try:

        raw_data = json.loads(
            input_path.read_text(
                encoding="utf-8-sig"
            )
        )

    except FileNotFoundError as exc:

        raise KnowledgeLoadError(
            f"Input JSON not found: "
            f"{input_path}"
        ) from exc

    except json.JSONDecodeError as exc:

        raise KnowledgeLoadError(
            f"Invalid JSON at line "
            f"{exc.lineno}, "
            f"column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    if not isinstance(
        raw_data,
        dict,
    ):
        raise KnowledgeLoadError(
            "INPUT.json root must be an object."
        )

    # --------------------------------------------------------
    # PUBLICATION DATE
    # --------------------------------------------------------

    publication_date = _required_text(
        raw_data,
        "publication_date",
        "INPUT.json",
    )

    publication_date_iso = _required_text(
        raw_data,
        "publication_date_iso",
        "INPUT.json",
    )

    # --------------------------------------------------------
    # EDITORIALS
    # --------------------------------------------------------

    editorials_raw = _required(
        raw_data,
        "editorials",
        "INPUT.json",
    )

    if not isinstance(
        editorials_raw,
        list,
    ):
        raise KnowledgeLoadError(
            "INPUT.json: "
            "'editorials' must be a list."
        )

    if not editorials_raw:
        raise KnowledgeLoadError(
            "INPUT.json must contain "
            "at least one editorial."
        )

    editorials = tuple(
        _load_editorial(
            editorial,
            position,
        )
        for position, editorial in enumerate(
            editorials_raw,
            start=1,
        )
    )

    return EditorialStudyData(
        publication_date=publication_date,
        publication_date_iso=publication_date_iso,
        editorials=editorials,
    )


# ============================================================
# CONVENIENCE LOADER
# ============================================================

def load_editorials(
    input_path: Path = INPUT_JSON,
) -> tuple[EditorialRecord, ...]:
    """
    Convenience function for PDF-generation code that
    needs only the editorial records.
    """

    return load_editorial_study_data(
        input_path
    ).editorials


# ============================================================
# OPTIONAL DIRECT TEST
# ============================================================

def main() -> int:

    try:

        data = load_editorial_study_data()

    except KnowledgeLoadError as exc:

        print()
        print(
            "KNOWLEDGE LOAD FAILED"
        )
        print(
            "---------------------"
        )
        print(
            exc
        )
        print()

        return 1

    print()
    print(
        "KNOWLEDGE LOAD SUCCESSFUL"
    )
    print(
        "-------------------------"
    )

    print(
        f"Date: "
        f"{data.publication_date}"
    )

    print(
        f"Editorials: "
        f"{len(data.editorials)}"
    )

    print()

    for editorial in data.editorials:

        print(
            f"{editorial.editorial_number}. "
            f"{editorial.heading} "
            f"({editorial.gs_paper})"
        )

        print(
            f"   Points: "
            f"{len(editorial.points)}"
        )

        print(
            f"   Anchors: "
            f"{len(editorial.anchors)}"
        )

    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )