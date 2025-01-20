import argparse
import logging
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

from tqdm import tqdm


def setup_logging(verbose=False):
    """
    Sets up the logging configuration.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def natural_sort_key(s):
    """
    Generates a key for natural sorting.
    Splits the string into a list of integers and non-integer substrings.
    """
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


def check_kcc_installed(project_root: Path) -> None:
    """
    Checks if 'kcc' is installed and available in the system's PATH.
    Exits the script if 'kcc' is not found.
    """
    if not shutil.which(project_root / "bin/kcc.exe"):
        logging.error(
            "'kcc' is not installed or not in PATH. Please install KCC and ensure it is in your PATH."
        )
        sys.exit(1)


def create_comic_info_xml(metadata: dict, output_path: Path) -> bool:
    """
    Generates a ComicInfo.xml file based on the provided metadata and saves it to output_path.
    :param metadata: Dictionary containing metadata fields.
    :param output_path: Path where ComicInfo.xml will be saved.
    :return: True if successful, False otherwise.
    """
    try:
        comic_info = ET.Element("ComicInfo")

        series = ET.SubElement(comic_info, "Series")
        series.text = metadata.get("title", "Unknown Series")

        summary = ET.SubElement(comic_info, "Summary")
        summary.text = metadata.get("summary", "No synopsis available.")

        # Create an ElementTree and write to file
        tree = ET.ElementTree(comic_info)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        logging.debug(f"Generated ComicInfo.xml at '{output_path}'.")
        return True
    except Exception as e:
        logging.error(f"Failed to generate ComicInfo.xml: {e}")
        return False


def generate_chapter_range(chapter_numbers: list[int]) -> str:
    """
    Generates a chapter range string given a list of chapter numbers.
    Example: [1, 2, 3, 4] -> "1 - 4"
    """
    if not chapter_numbers:
        return "Unknown Chapters"
    min_chapter_num, max_chapter_num = min(chapter_numbers), max(chapter_numbers)
    return f"{int(min_chapter_num)} - {int(max_chapter_num)}"


def parse_arguments():
    """
    Parse command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process a folder containing manga chapters in CBZ format."
    )
    parser.add_argument(
        "root_folder_path",
        type=str,
        default=Path.cwd(),
        nargs="?",
        help="Path to the folder containing manga chapters in CBZ format.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without making any changes.",
    )
    return parser.parse_args()


def get_sorted_cbz_files(directory: Path) -> list[Path]:
    """
    Retrieves and sorts all CBZ files in the given directory using natural sorting.
    Returns a list of Path objects.
    """
    cbz_files = sorted(directory.glob("*.cbz"), key=lambda x: natural_sort_key(x.name))
    logging.info(f"Found {len(cbz_files)} CBZ files.")
    return cbz_files


def create_output_folder(dir: Path) -> Path:
    """
    Creates a new directory named 'converted' inside the given directory.
    Returns the Path object of the newly created directory.
    """
    converted_output_dir = dir / "Converted"
    try:
        converted_output_dir.mkdir(exist_ok=True)
    except Exception as e:
        logging.error(
            f"Failed to create output directory '{converted_output_dir}': {e}"
        )
        return False
    return converted_output_dir


def clean_cover_image(dry_run, cover_image_path) -> bool:
    # Clean up the cover image temp file if it was created

    if cover_image_path and cover_image_path.exists() and not dry_run:
        try:
            cover_image_path.unlink()
            logging.info(f"Deleted temporary cover image file: {cover_image_path}")
        except Exception as e:
            logging.error(
                f"Failed to delete temporary cover image file '{cover_image_path}': {e}"
            )
            return False
    return True


def zip_files(output_cbz_path, files_to_zip):
    with zipfile.ZipFile(output_cbz_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in tqdm(files_to_zip, desc="Adding Files to CBZ", unit="file"):
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
