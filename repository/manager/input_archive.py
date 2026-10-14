"""Archive the exact daily input text after a successful OnePage Study run."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_TEXT = PROJECT_ROOT / "INPUT_DATA.txt"
INPUT_JSON = PROJECT_ROOT / "input_processing" / "INPUT.json"
ARCHIVE_ROOT = PROJECT_ROOT / "repository" / "input_data"


def archive_input() -> Path:
    if not INPUT_JSON.is_file():
        raise FileNotFoundError(f"Validated input JSON not found: {INPUT_JSON}")
    if not INPUT_TEXT.is_file():
        raise FileNotFoundError(f"Original input text not found: {INPUT_TEXT}")

    data = json.loads(INPUT_JSON.read_text(encoding="utf-8-sig"))
    publication_date = datetime.strptime(data["publication_date"], "%d %B %Y")
    raw_bytes = INPUT_TEXT.read_bytes()
    if not raw_bytes.strip():
        raise ValueError("INPUT_DATA.txt is empty; refusing to replace an archive.")

    folder = ARCHIVE_ROOT / str(publication_date.year) / publication_date.strftime("%m_%B")
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"UAK_Input_{publication_date:%y%m%d}.txt"

    # Write to a temporary file first, then atomically replace any existing
    # archive for this publication date. The input bytes are not altered.
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=folder, prefix=".input_", suffix=".tmp", delete=False) as tmp:
            temporary_path = Path(tmp.name)
            tmp.write(raw_bytes)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return destination


def main() -> int:
    destination = archive_input()
    print(f"Input data archived: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
