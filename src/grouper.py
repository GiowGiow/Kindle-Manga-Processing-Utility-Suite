import logging
from pathlib import Path
import shutil
import tempfile

from tqdm import tqdm
from .constants import (
    CHAPTERS_PER_PART,
    IMAGE_EXTENSIONS,
)

from .extractor import extract_cbz
from .parser import parse_chapter_number
from .state_manager import part_already_processed
from .utils import natural_sort_key, zip_files


def create_combined_cbz(temp_dir: Path, output_cbz_path: Path) -> bool:
    """
    Creates a combined CBZ file from all images in temp_dir.
    Returns True if creation is successful, False otherwise.
    """
    files_to_zip = sorted(temp_dir.glob("*"), key=lambda x: natural_sort_key(x.name))
    total_files = len(files_to_zip)

    if total_files == 0:
        logging.error("No files to add to the combined CBZ.")
        return False

    logging.info(
        f"Creating combined CBZ with {total_files} files as '{output_cbz_path.name}'."
    )
    try:
        zip_files(output_cbz_path, files_to_zip)
    except Exception as e:
        logging.error(f"Failed to create combined CBZ '{output_cbz_path.name}': {e}")
        return False

    logging.info(f"Successfully created '{output_cbz_path.name}'.")
    return True


def combine_to_cbz(
    status,
    status_file,
    chapter_range,
    part_cbz_files,
    output_cbz_path,
    output_cbz_name,
    cover_image_path,
) -> bool:
    # Check if this part has already been processed for CBZ combining
    if part_already_processed(status, chapter_range):
        logging.info(
            f"Chapters {chapter_range} already combined into CBZ. Skipping CBZ combining."
        )
        return True

    with tempfile.TemporaryDirectory() as tmp_dir:
        logging.info(f"Chapter range: {chapter_range}")
        temp_dir_path = Path(tmp_dir)

        logging.info(
            f"Collecting chapter images for chapters {chapter_range} in temporary directory: {temp_dir_path}"
        )

        insert_cover = cover_image_path is not None

        image_count = get_pack_images_to_tmp_dir(
            part_cbz_files,
            temp_dir_path,
            cover_image_path=cover_image_path,
            insert_cover=insert_cover,
        )

        if image_count == 0:
            logging.error("No images collected; skipping this part.")
            return

        success = create_combined_cbz(temp_dir_path, output_cbz_path)
        return success


def get_pack_images_to_tmp_dir(
    part_cbz_files: list[Path],
    temp_dir: Path,
    cover_image_path: Path = None,
    insert_cover: bool = False,
) -> int:
    """
    Extracts and collects all images from the chapters in `part_cbz_files` into `temp_dir`.
    If cover_image_path is provided and insert_cover is True, this cover image is inserted once at the start of the final sequence.
    Returns the total number of images collected.
    """
    image_count = 0

    # Insert cover as the *very first image* of the entire sequence (once only)
    if cover_image_path and insert_cover and cover_image_path.exists():
        image_count += 1
        cover_dest = temp_dir / f"{image_count:05d}_cover{cover_image_path.suffix}"
        try:
            shutil.copy2(cover_image_path, cover_dest)
            logging.debug("Inserted cover image at the start of this part.")
        except Exception as e:
            logging.error(f"Failed to copy cover image: {e}")

    for cbz in tqdm(part_cbz_files, desc="Processing Chapters", unit="chapter"):
        chapter_extract_dir = temp_dir / cbz.stem
        success = extract_cbz(cbz, chapter_extract_dir)
        if not success:
            continue

        # Get all image files in the chapter directory, sorted naturally
        images = get_sorted_images(chapter_extract_dir)

        if not images:
            logging.warning(f"No images found in '{cbz.name}'.")
            continue

        for img in images:
            image_count += 1
            new_name = f"{image_count:05d}_{img.name}"
            destination = temp_dir / new_name
            try:
                shutil.copy2(img, destination)
            except Exception as e:
                logging.error(f"Failed to copy image '{img.name}': {e}")

    logging.info(f"Total images collected for this part: {image_count}")
    return image_count


def get_sorted_images(chapter_extract_dir):
    return sorted(
        [
            image
            for image in chapter_extract_dir.iterdir()
            if image.suffix.lower() in IMAGE_EXTENSIONS
        ],
        key=lambda x: natural_sort_key(x.name),
    )


def group_cbz_into_packs(
    cbz_files: list[Path], chapters_per_part: int = CHAPTERS_PER_PART
) -> list[list[Path]]:
    """
    Groups CBZ files into parts, each containing up to chapters_per_part chapters.
    Returns a list of lists, where each sublist contains CBZ Path objects.
    """
    # Sort CBZ files based on chapter number
    sorted_cbz_files = sorted(
        cbz_files, key=lambda cbz: parse_chapter_number(cbz.name) or 0
    )

    cbz_packs = [
        sorted_cbz_files[i : i + chapters_per_part]
        for i in range(0, len(sorted_cbz_files), chapters_per_part)
    ]

    logging.info(
        f"Organized CBZ files into {len(cbz_packs)} parts with up to {chapters_per_part} chapters each."
    )
    return cbz_packs
