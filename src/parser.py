import logging
from pathlib import Path
import re

MANGA_CHAPTER_PATTERN = re.compile(r"([\d]+.?\d*)\.cbz", re.IGNORECASE)
MANGA_NAME_PATTERN = re.compile(
    r"^(.*?)\s*Chapter[\s\-_]*[\d\.]+.*\.cbz$", re.IGNORECASE
)


def parse_chapter_number(filename):
    """
    Extracts the chapter number from a CBZ filename.
    Handles formats like:
        - 'Chapter 125.cbz'
        - 'Chapter125.cbz'
        - 'Chapter 125.5.cbz'
        - 'Manga Name Chapter 125.cbz'
        - 'Manga Name Chapter125.5.cbz'
    Returns a float representing the chapter number, or None if not found.
    """
    # Improved regex to handle optional space or delimiter between 'Chapter' and number
    match = re.search(MANGA_CHAPTER_PATTERN, filename)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            logging.warning(f"Invalid chapter number format in filename '{filename}'.")
            return None
    logging.warning(f"No chapter number found in filename '{filename}'.")
    return None


def get_manga_name(directory: Path, cbz_files: list[Path]) -> str:
    """
    Attempts to parse the manga name from the CBZ filenames.
    If CBZ filenames include the manga name (e.g., 'Manga Name Chapter 1.cbz'),
    it extracts the manga name. Otherwise, it uses the directory name.
    """
    if not cbz_files:
        return None

    first_cbz = cbz_files[0].name
    # Attempt to extract manga name from the first CBZ filename
    # Example: 'Manga Name Chapter 1.cbz' -> 'Manga Name'
    match = re.match(MANGA_NAME_PATTERN, first_cbz)
    if match and match.group(1).strip():
        return match.group(1).strip()
    else:
        # Fallback to directory name
        return directory.name


def is_volume(chapter_number: int, manga_name: str) -> bool:
    """
    Determines if a CBZ file is part of a volume based on its filename.
    Adjust this function if your naming convention differs.
    """
    return False
