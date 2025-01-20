import logging
from pathlib import Path
import subprocess
import zipfile

from .utils import create_comic_info_xml


def convert_cbz_to_mobi(
    project_root: Path, cbz_path: Path, author, title, metadata: dict
) -> bool:
    """
    Calls KCC via subprocess to convert a .cbz file to Kindle format (MOBI).
    Adds metadata (author, title, etc.), uses KPW5 profile, etc.
    Returns True if conversion is successful, False otherwise.
    """
    # Generate ComicInfo.xml and add it to the CBZ
    comic_info_path = cbz_path.parent / "ComicInfo.xml"

    if not create_comic_info_xml(metadata, comic_info_path):
        logging.error("Failed to create ComicInfo.xml. Skipping KCC conversion.")
        return False

    # Ensure ComicInfo.xml is inside the CBZ
    try:
        with zipfile.ZipFile(cbz_path, "a") as zipf:
            zipf.write(comic_info_path, "ComicInfo.xml")
        logging.debug(f"Added ComicInfo.xml to '{cbz_path.name}'.")
    except Exception as e:
        logging.error(f"Failed to add ComicInfo.xml to '{cbz_path.name}': {e}")
        return False

    kcc_path = str(project_root / "bin" / "kcc.exe")
    # Define the KCC command
    kcc_cmd = [
        kcc_path,
        "-p",
        "KPW5",  # Profile for Kindle Paperwhite
        "-f",
        "MOBI",
        "-m",  # Manga mode (right-to-left)
        "--stretch",
        "--author",
        author,
        "--title",
        title,
        "--dedupecover",
        str(cbz_path),
    ]

    logging.info(f"Running KCC command: {' '.join(kcc_cmd)}")
    try:
        subprocess.run(kcc_cmd, check=True)
        logging.info(f"KCC conversion succeeded for '{cbz_path.name}'.")
        if comic_info_path.exists():
            comic_info_path.unlink()
            logging.debug(f"Deleted temporary ComicInfo.xml file: {comic_info_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"KCC conversion failed for '{cbz_path.name}': {e}")
    except FileNotFoundError:
        logging.error(
            "KCC executable not found. Please ensure KCC is installed and in your PATH."
        )
    return False
