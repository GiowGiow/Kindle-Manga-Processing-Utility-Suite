import logging
from pathlib import Path
import shutil
import tempfile
import zipfile

from .constants import IMAGE_EXTENSIONS
from .manga_info import download_cover_image
from .utils import natural_sort_key


def extract_cbz(cbz_path: Path, extract_to: Path) -> bool:
    """
    Extracts a CBZ file to the specified directory.
    Returns True if extraction is successful, False otherwise.
    """
    try:
        with zipfile.ZipFile(cbz_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        logging.debug(f"Extracted '{cbz_path.name}' to '{extract_to}'.")
        return True
    except zipfile.BadZipFile:
        logging.error(f"Failed to extract '{cbz_path.name}': Bad zip file.")
    except Exception as e:
        logging.error(f"Failed to extract '{cbz_path.name}': {e}")
    return False


def extract_and_save_cover_image(
    cbz_files: list[Path], manga_name: str, fetch: bool, cover_image_url: str
) -> Path | None:
    """
    Assumes the first image of the *first chapter* in the entire manga is the cover image.
    Extracts and saves the cover image to a temporary file without using Pillow.
    Returns the Path to the cover image file.
    """
    if not cbz_files:
        logging.error("No CBZ files provided to extract_and_save_cover_image.")
        return None

    if fetch and cover_image_url:
        return download_cover_image(cover_image_url, manga_name)

    return extract_first_cover_image(cbz_files)


def extract_first_cover_image(cbz_files: list[Path]) -> Path | None:
    first_chapter = cbz_files[0]
    try:
        with zipfile.ZipFile(first_chapter, "r") as cbz:
            file_list = cbz.namelist()

            # Filter image files only
            image_files = sorted(
                [file for file in file_list if file.lower().endswith(IMAGE_EXTENSIONS)],
                key=natural_sort_key,
            )

            if not image_files:
                logging.warning(f"No image files found in '{first_chapter}'.")
                return None

            first_image_file = image_files[0]
            image_extension = Path(first_image_file).suffix

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=image_extension
            ) as cover_tmp:
                cover_image_path = Path(cover_tmp.name)
                logging.info(
                    f"Extracting cover image from '{first_chapter.name}': {cover_image_path}..."
                )

            with cbz.open(first_image_file) as image_file, open(
                cover_image_path, "wb"
            ) as out_file:
                shutil.copyfileobj(image_file, out_file)

        logging.debug(f"Cover image extracted and saved to '{cover_image_path}'.")
        return cover_image_path
    except zipfile.BadZipFile:
        logging.error(f"Invalid CBZ file: {first_chapter}")
    except Exception as e:
        logging.error(f"Error extracting cover image from '{first_chapter}': {e}")
        return None
