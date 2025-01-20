import json
import logging
from pathlib import Path


def load_status(current_dir, status_file_path: Path) -> dict:
    """
    Loads the processing status from a JSON file.
    Uses chapter ranges as keys.
    If the file does not exist, returns an empty status.
    """
    status_file_path = current_dir / status_file_path

    if not status_file_path.exists():
        logging.info(
            f"Status file '{status_file_path}' does not exist. Initializing new status."
        )
        return {"processed_cbz_parts": {}, "converted_mobi_parts": {}}, status_file_path
    try:
        with open(status_file_path, "r", encoding="utf-8") as f:
            status = json.load(f)
        logging.debug(f"Loaded processing status from '{status_file_path}'.")
        return status, status_file_path
    except Exception as e:
        logging.error(f"Failed to load status file '{status_file_path}': {e}")
        return {"processed_cbz_parts": {}, "converted_mobi_parts": {}}, status_file_path


def save_status(status_file: Path, status: dict):
    """
    Saves the processing status to a JSON file atomically.
    """
    try:
        temp_file = status_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)
        temp_file.replace(status_file)
        logging.debug(f"Saved processing status to '{status_file}'.")
    except Exception as e:
        logging.error(f"Failed to save status file '{status_file}': {e}")


def update_conversion_status(status_file, status, chapter_range):
    status.setdefault("converted_mobi_parts", {})[chapter_range] = True
    save_status(status_file, status)


def update_status(status_file, status, chapter_range):
    status.setdefault("processed_cbz_parts", {})[chapter_range] = True
    save_status(status_file, status)


def part_already_converted_to_mobi(status: dict, chapter_range):
    return chapter_range in status.get("converted_mobi_parts", {})


def part_already_processed(status: dict, chapter_range):
    return chapter_range in status.get("processed_cbz_parts", {})
