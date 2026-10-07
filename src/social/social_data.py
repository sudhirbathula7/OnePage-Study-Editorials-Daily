from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from src.config import INPUT_PATH
from src.social.social_config import (
    ANCHORS_PER_EDITORIAL,
    MAX_EDITORIALS,
)


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SocialEditorial:
    question: str
    anchors: tuple[str, str, str, str]


@dataclass(frozen=True)
class SocialImageData:
    publication_date: str
    publication_date_iso: str
    display_date: str
    editorials: tuple[SocialEditorial, ...]


# ============================================================
# BASIC HELPERS
# ============================================================

def _required_text(value: object, field_name: str) -> str:
    """
    Return a cleaned string or raise an error when a required
    social-image field is missing.
    """

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return value


def _format_display_date(
    publication_date: str,
    publication_date_iso: str,
) -> str:
    """
    Convert the publication date into a clean social-post date.

    Preferred output:
        07 October 2026
    """

    candidates = (
        publication_date_iso,
        publication_date,
    )

    formats = (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    )

    for candidate in candidates:
        if not isinstance(candidate, str):
            continue

        candidate = candidate.strip()

        if not candidate:
            continue

        for date_format in formats:
            try:
                parsed = datetime.strptime(
                    candidate,
                    date_format,
                )

                return parsed.strftime(
                    "%d %B %Y"
                )

            except ValueError:
                continue

    # If the date cannot be converted, preserve the original
    # publication date instead of inventing a new value.
    return publication_date


# ============================================================
# EDITORIAL EXTRACTION
# ============================================================

def _load_social_editorial(
    raw_editorial: object,
    position: int,
) -> SocialEditorial:
    """
    Extract the Question and four existing Recall Anchors
    from one editorial record.
    """

    if not isinstance(raw_editorial, dict):
        raise ValueError(
            f"Editorial {position} must be an object."
        )

    question = _required_text(
        raw_editorial.get("question"),
        f"Editorial {position} question",
    )

    raw_anchors = raw_editorial.get("anchors")

    if not isinstance(raw_anchors, list):
        raise ValueError(
            f"Editorial {position} anchors must be a list."
        )

    if len(raw_anchors) != ANCHORS_PER_EDITORIAL:
        raise ValueError(
            f"Editorial {position} must contain exactly "
            f"{ANCHORS_PER_EDITORIAL} anchors."
        )

    anchors = tuple(
        _required_text(
            anchor,
            f"Editorial {position} anchor {index}",
        )
        for index, anchor in enumerate(
            raw_anchors,
            start=1,
        )
    )

    return SocialEditorial(
        question=question,
        anchors=anchors,  # type: ignore[arg-type]
    )


# ============================================================
# MAIN DATA LOADER
# ============================================================

def load_social_image_data(
    input_path: Path | str = INPUT_PATH,
) -> SocialImageData:
    """
    Load social-image content directly from the existing
    INPUT.json.

    No separate social input file is required.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"INPUT.json not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            raw_data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path}: {exc}"
        ) from exc

    if not isinstance(raw_data, dict):
        raise ValueError(
            "INPUT.json root must be an object."
        )

    publication_date = _required_text(
        raw_data.get("publication_date"),
        "publication_date",
    )

    publication_date_iso = _required_text(
        raw_data.get("publication_date_iso"),
        "publication_date_iso",
    )

    raw_editorials = raw_data.get("editorials")

    if not isinstance(raw_editorials, list):
        raise ValueError(
            "editorials must be a list."
        )

    if not raw_editorials:
        raise ValueError(
            "At least one editorial is required "
            "for the social image."
        )

    # The OnePage social post is designed for a maximum
    # of four editorials.
    selected_editorials = raw_editorials[
        :MAX_EDITORIALS
    ]

    editorials = tuple(
        _load_social_editorial(
            raw_editorial,
            position,
        )
        for position, raw_editorial in enumerate(
            selected_editorials,
            start=1,
        )
    )

    display_date = _format_display_date(
        publication_date,
        publication_date_iso,
    )

    return SocialImageData(
        publication_date=publication_date,
        publication_date_iso=publication_date_iso,
        display_date=display_date,
        editorials=editorials,
    )


# ============================================================
# QUICK MANUAL TEST
# ============================================================

def main() -> None:
    data = load_social_image_data()

    print()
    print("SOCIAL IMAGE DATA")
    print("=" * 60)

    print(
        f"Publication Date : {data.publication_date}"
    )
    print(
        f"ISO Date         : {data.publication_date_iso}"
    )
    print(
        f"Display Date     : {data.display_date}"
    )
    print(
        f"Editorials       : {len(data.editorials)}"
    )

    for index, editorial in enumerate(
        data.editorials,
        start=1,
    ):
        print()
        print(f"QUESTION {index}")
        print(editorial.question)

        print("ANCHORS")
        print(
            "  •  ".join(editorial.anchors)
        )

    print()
    print("Social image data loaded successfully.")


if __name__ == "__main__":
    main()