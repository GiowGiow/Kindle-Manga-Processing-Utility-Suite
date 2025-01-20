import argparse
from pathlib import Path
import logging
from combine_and_process_cbz import process_manga_folder, setup_logging


def process_all_manga_folders(parent_dir: Path, dry_run: bool):
    """
    Iterates over all subdirectories in `parent_dir` and processes each as a manga folder.
    """
    logging.info(f"Processing all folders in '{parent_dir}'...")
    for subdir in parent_dir.iterdir():
        if subdir.is_dir():
            # Check if the subdir has .cbz files (optional)
            cbz_files = list(subdir.glob("*.cbz"))
            if cbz_files:
                process_manga_folder(subdir, dry_run)
            else:
                logging.info(f"Skipping folder (no CBZ files found): {subdir}")


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
        help="Path to the folder containing manga chapters in CBZ format.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without making any changes.",
    )
    return parser.parse_args()


def main():
    setup_logging(verbose=False)
    args = parse_arguments()
    dry_run = args.dry_run
    root_folder_path = Path(args.root_folder_path)
    process_all_manga_folders(root_folder_path, dry_run=dry_run)

    logging.info("All manga folders have been processed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Script interrupted by user. Exiting...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
