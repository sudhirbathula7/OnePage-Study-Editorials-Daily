import json
import sys

from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_JSON_PATH = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def _is_nonempty_string(
    value: Any,
) -> bool:
    """
    Check only whether a value is usable text.

    No word-count or wording restrictions are applied.
    """

    return (
        isinstance(value, str)
        and bool(value.strip())
    )


# ============================================================
# EDITORIAL VALIDATION
# ============================================================

def _validate_editorial(
    editorial: dict[str, Any],
    expected_number: int,
) -> list[str]:

    errors: list[str] = []

    editorial_number = editorial.get(
        "editorial_number"
    )

    # --------------------------------------------------------
    # EDITORIAL NUMBER
    # --------------------------------------------------------

    if not isinstance(
        editorial_number,
        int,
    ):
        errors.append(
            f"Editorial {expected_number}: "
            "editorial_number must be an integer."
        )

    elif editorial_number != expected_number:
        errors.append(
            f"Editorial position {expected_number}: "
            f"expected editorial_number "
            f"{expected_number}, found "
            f"{editorial_number}."
        )

    # --------------------------------------------------------
    # SIMPLE TEXT FIELDS
    # --------------------------------------------------------

    for field in (
        "heading",
        "gs_paper",
        "question",
        "takeaway",
    ):

        if not _is_nonempty_string(
            editorial.get(field)
        ):
            errors.append(
                f"Editorial {expected_number}: "
                f"'{field}' cannot be empty."
            )

    # --------------------------------------------------------
    # POINTS
    # --------------------------------------------------------

    points = editorial.get(
        "points"
    )

    if not isinstance(
        points,
        list,
    ):
        errors.append(
            f"Editorial {expected_number}: "
            "'points' must be a list."
        )

        return errors

    if len(points) != 4:
        errors.append(
            f"Editorial {expected_number}: "
            "exactly 4 points are required. "
            f"Found {len(points)}."
        )

    # --------------------------------------------------------
    # ANCHORS
    # --------------------------------------------------------

    anchors = editorial.get(
        "anchors"
    )

    if not isinstance(
        anchors,
        list,
    ):
        errors.append(
            f"Editorial {expected_number}: "
            "'anchors' must be a list."
        )

        anchors = []

    elif len(anchors) != 4:
        errors.append(
            f"Editorial {expected_number}: "
            "exactly 4 anchors are required. "
            f"Found {len(anchors)}."
        )

    # --------------------------------------------------------
    # INDIVIDUAL POINTS
    # --------------------------------------------------------

    for position, point in enumerate(
        points,
        start=1,
    ):

        if not isinstance(
            point,
            dict,
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                "must be an object."
            )

            continue

        point_number = point.get(
            "number"
        )

        point_text = point.get(
            "text"
        )

        point_anchor = point.get(
            "anchor"
        )

        if not isinstance(
            point_number,
            int,
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                "'number' must be an integer."
            )

        elif point_number != position:
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                f"expected number {position}, "
                f"found {point_number}."
            )

        if not _is_nonempty_string(
            point_text
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                "text cannot be empty."
            )

        if not _is_nonempty_string(
            point_anchor
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                "anchor cannot be empty."
            )

        # ----------------------------------------------------
        # ANCHOR MUST EXIST INSIDE ITS POINT
        # ----------------------------------------------------
        #
        # This is not a wording restriction.
        #
        # It only ensures that the PDF can safely highlight
        # the manually selected anchor inside the point.
        # ----------------------------------------------------

        if (
            _is_nonempty_string(point_text)
            and
            _is_nonempty_string(point_anchor)
            and
            point_anchor.casefold()
            not in point_text.casefold()
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                f"anchor '{point_anchor}' "
                "does not occur inside the point text."
            )

        # ----------------------------------------------------
        # POINT ANCHOR SHOULD MATCH ANCHORS LIST
        # ----------------------------------------------------

        if (
            position <= len(anchors)
            and
            _is_nonempty_string(
                anchors[position - 1]
            )
            and
            _is_nonempty_string(
                point_anchor
            )
            and
            anchors[position - 1].casefold()
            != point_anchor.casefold()
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Point {position}: "
                "point anchor does not match "
                "the corresponding anchor "
                "in the anchors list."
            )

    # --------------------------------------------------------
    # ANCHOR LIST CONTENT
    # --------------------------------------------------------

    for position, anchor in enumerate(
        anchors,
        start=1,
    ):

        if not _is_nonempty_string(
            anchor
        ):
            errors.append(
                f"Editorial {expected_number}, "
                f"Anchor {position}: "
                "cannot be empty."
            )

    return errors


# ============================================================
# COMPLETE JSON VALIDATION
# ============================================================

def validate_data(
    data: Any,
) -> list[str]:

    errors: list[str] = []

    # --------------------------------------------------------
    # ROOT
    # --------------------------------------------------------

    if not isinstance(
        data,
        dict,
    ):
        return [
            "Root JSON must be an object."
        ]

    # --------------------------------------------------------
    # PUBLICATION DATE
    # --------------------------------------------------------

    if not _is_nonempty_string(
        data.get("publication_date")
    ):
        errors.append(
            "'publication_date' cannot be empty."
        )

    if not _is_nonempty_string(
        data.get("publication_date_iso")
    ):
        errors.append(
            "'publication_date_iso' cannot be empty."
        )

    # --------------------------------------------------------
    # EDITORIALS
    # --------------------------------------------------------

    editorials = data.get(
        "editorials"
    )

    if not isinstance(
        editorials,
        list,
    ):
        errors.append(
            "'editorials' must be a list."
        )

        return errors

    if not editorials:
        errors.append(
            "At least one editorial is required."
        )

        return errors

    # --------------------------------------------------------
    # EDITORIAL COUNT
    # --------------------------------------------------------

    editorial_count = data.get(
        "editorial_count"
    )

    if not isinstance(
        editorial_count,
        int,
    ):
        errors.append(
            "'editorial_count' must be an integer."
        )

    elif editorial_count != len(
        editorials
    ):
        errors.append(
            "'editorial_count' does not match "
            "the number of editorials."
        )

    # --------------------------------------------------------
    # INDIVIDUAL EDITORIALS
    # --------------------------------------------------------

    for position, editorial in enumerate(
        editorials,
        start=1,
    ):

        if not isinstance(
            editorial,
            dict,
        ):
            errors.append(
                f"Editorial position {position}: "
                "must be an object."
            )

            continue

        errors.extend(
            _validate_editorial(
                editorial,
                position,
            )
        )

    return errors


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_file(
    input_path: Path = INPUT_JSON_PATH,
) -> bool:

    print()
    print(
        "=" * 64
    )
    print(
        "VALIDATING INPUT.json"
    )
    print(
        "=" * 64
    )

    if not input_path.exists():

        print(
            f"ERROR: File not found: "
            f"{input_path}"
        )

        return False

    try:

        with input_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

    except json.JSONDecodeError as exc:

        print(
            "ERROR: INPUT.json contains invalid JSON."
        )

        print(
            f"Line {exc.lineno}, "
            f"column {exc.colno}: "
            f"{exc.msg}"
        )

        return False

    except OSError as exc:

        print(
            "ERROR: Could not read INPUT.json: "
            f"{exc}"
        )

        return False

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    errors = validate_data(
        data
    )

    if errors:

        print()
        print(
            "VALIDATION FAILED"
        )
        print(
            "-----------------"
        )

        print(
            f"Total errors: {len(errors)}"
        )

        print()

        for index, error in enumerate(
            errors,
            start=1,
        ):

            print(
                f"{index}. {error}"
            )

        print()

        return False

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    editorials = data.get(
        "editorials",
        [],
    )

    print()
    print(
        "INPUT.json validation PASSED."
    )

    print(
        f"Editorials validated: "
        f"{len(editorials)}"
    )

    print()

    for editorial in editorials:

        number = editorial.get(
            "editorial_number"
        )

        heading = editorial.get(
            "heading"
        )

        gs_paper = editorial.get(
            "gs_paper"
        )

        print(
            f"{number}. "
            f"{heading} "
            f"({gs_paper})"
        )

    print()

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    success = validate_file()

    if success:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )