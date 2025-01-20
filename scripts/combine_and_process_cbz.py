#!/usr/bin/env python3

import sys
from pathlib import Path

# Determine the project root based on the script's location
project_root = Path(__file__).resolve().parent.parent

# Add the project root to sys.path
sys.path.append(str(project_root))

import logging
from src.constants import CHAPTERS_PER_PART, STATUS_FILE
from src.cbz_convertor import convert_cbz_to_mobi
from src.extractor import extract_and_save_cover_image
from src.grouper import combine_to_cbz, group_cbz_into_packs
from src.parser import get_manga_name, parse_chapter_number
from src.utils import (
    check_kcc_installed,
    clean_cover_image,
    create_output_folder,
    generate_chapter_range,
    get_sorted_cbz_files,
    parse_arguments,
    setup_logging,
)
from src.manga_info import fetch_manga_info_jikan
from src.state_manager import (
    load_status,
    part_already_converted_to_mobi,
    update_conversion_status,
    update_status,
)
from rich.console import Console
from rich.table import Table
from rich.text import Text
from textual_image.renderable import Image

console = Console()


def create_ascii_art(image_path: Path):
    try:
        output = AsciiArt.from_image(image_path)
        ascii_art_str = output.to_ascii(columns=80)
        return ascii_art_str
    except Exception as e:
        logging.error(f"Failed to display ASCII art: {e}")


def display_manga_info(metadata: dict, ascii_art_path):
    """
    metadata= {
        "title": manga_title,
        "author": author_str,
        "summary": synopsis,
        "genres": genres_str,
        "score": score,
        "cover_image_url": cover_image_url,
    }
    """
    table = Table(
        title="📚 Manga Information",
        show_header=True,
        header_style="bold magenta",
    )

    # Define table columns
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Details", style="white")

    # Add rows to the table
    table.add_row("Title", metadata.get("title", "N/A"))
    table.add_row("Author(s)", metadata.get("author", "N/A"))
    table.add_row("Score", str(metadata.get("score", "N/A")))
    table.add_row(
        "Genres",
        metadata.get("genres") if metadata.get("genres") else "N/A",
    )
    table.add_row("Synopsis", Text(metadata.get("summary", "N/A"), style="dim"))
    table.add_row("Cover Image", metadata.get("cover_image_url", "N/A"))
    table.add_row("ASCII Art", Image(ascii_art_path))

    # Display the table and ASCII art side by side
    console.print(table)
    # Add additional fields as needed
    # Example: table.add_row("Publication Date", metadata.get("publication_date", "N/A"))


def process_manga_folder(dir: Path, dry_run: bool) -> None:
    logging.info(f"Scanning directory: {dir}")

    cbz_files = get_sorted_cbz_files(dir)
    if not cbz_files:
        logging.error("No CBZ files found in the current directory.")
        return

    manga_name = get_manga_name(dir, cbz_files)
    if not manga_name:
        logging.error("Unable to determine manga name from the CBZ files.")
        return
    logging.debug(f"Possible manga name: '{manga_name}'")
    logging.info(f"Fetching metadata on Jikan for '{manga_name}'...")
    metadata = fetch_manga_info_jikan(manga_name)
    if not metadata:
        logging.error("Failed to retrieve manga information from Jikan API.")
        return

    # Get the cover image as a Path (from the first CBZ)
    cover_image_path = (
        extract_and_save_cover_image(
            cbz_files,
            manga_name,
            fetch=True,
            cover_image_url=metadata["cover_image_url"],
        )
        if not dry_run
        else None
    )

    display_manga_info(metadata, cover_image_path)
    cbz_packs = group_cbz_into_packs(cbz_files, chapters_per_part=CHAPTERS_PER_PART)

    total_num_of_packs = len(cbz_packs)

    converted_output_folder = create_output_folder(dir)
    status, status_file_path = load_status(dir, STATUS_FILE)
    processed_status = (
        "None" if not status["processed_cbz_parts"] else status["processed_cbz_parts"]
    )
    converted_status = (
        "None" if not status["converted_mobi_parts"] else status["converted_mobi_parts"]
    )
    logging.info(f"Processed: {processed_status}")
    logging.info(f"Converted: {converted_status}")

    author_str = metadata["author"]
    process_packs(
        dry_run,
        manga_name,
        metadata,
        author_str,
        cbz_packs,
        total_num_of_packs,
        converted_output_folder,
        status_file_path,
        status,
        cover_image_path,
    )

    clean_cover_image(dry_run, cover_image_path)
    logging.info("All parts have been processed and converted successfully.")


def process_packs(
    dry_run,
    manga_name,
    metadata,
    author_str,
    parts,
    total_parts,
    converted_output_dir,
    status_file_path,
    status,
    cover_image_path,
):
    for part_number, part_cbz_files in enumerate(parts, start=1):
        logging.info(
            f"Processing Part {part_number}/{total_parts} with {len(part_cbz_files)} chapters."
        )

        chapter_numbers = [
            parse_chapter_number(cbz.name) or 0 for cbz in part_cbz_files
        ]

        logging.info(f"Chapter numbers: {chapter_numbers}")
        chapter_range = generate_chapter_range(chapter_numbers)

        output_cbz_name = f"{manga_name} {chapter_range}.cbz"
        output_cbz_path = converted_output_dir / output_cbz_name

        if dry_run:
            if part_number in status.get("processed_cbz_parts", []):
                logging.info(
                    "[Dry Run] Already processed CBZ, would skip CBZ combining for this part."
                )
            logging.info(f"[Dry Run] Would process chapters {chapter_range}.")
            continue

        success = combine_to_cbz(
            status,
            status_file_path,
            chapter_range,
            part_cbz_files,
            output_cbz_path,
            output_cbz_name,
            cover_image_path,
        )
        if not success:
            logging.error(f"Failed to create '{output_cbz_name}'.")
            continue

        # Update status using chapter_range as key
        update_status(status_file_path, status, chapter_range)

        if part_already_converted_to_mobi(status, chapter_range):
            logging.info(
                f"Chapters {chapter_range} already converted to MOBI. Skipping conversion."
            )
            continue

        success = convert_cbz_to_mobi(
            project_root,
            output_cbz_path,
            author=author_str,
            title=f"{manga_name} {chapter_range}",
            metadata=metadata,
        )

        if success:
            update_conversion_status(status_file_path, status, chapter_range)
        else:
            logging.error(f"Failed to convert Part {part_number} to MOBI.")


def main() -> None:
    setup_logging(verbose=False)
    check_kcc_installed(project_root)
    args = parse_arguments()
    directory = Path(args.root_folder_path).resolve()
    dry_run = args.dry_run
    process_manga_folder(directory, dry_run)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Script interrupted by user. Exiting...")
