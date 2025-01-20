import subprocess
from pathlib import Path
import sys
import argparse

from src.utils import natural_sort_key


def add_mobi_with_calibredb(calibredb_path: str, mobi_file: Path):
    """
    Adds a .mobi file to Calibre library using calibredb add command.

    :param calibredb_path: Path to the calibredb executable.
    :param library_path: Path to the Calibre library.
    :param mobi_file: Path to the .mobi file to be added.
    :return: Tuple containing (success: bool, message: str)
    """
    try:
        command = [
            "calibredb",
            str(calibredb_path),
            "add",
            str(mobi_file),
        ]
        print(command)
        # Execute the command
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()

    except Exception as e:
        return False, str(e)


def parse_arguments():
    """
    Parse command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Add all .mobi files from a specified folder to a Calibre library using calibredb."
    )
    parser.add_argument(
        "root_folder_path",
        type=str,
        help="Path to the folder containing .mobi files to be added.",
    )
    parser.add_argument(
        "--calibredb-path",
        type=str,
        default="C:/Users/giomartinelli/Calibre Library",
        help="Path to the calibredb executable. Default: calibredb",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate adding books without making any changes.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Resolve paths
    root_folder_path = Path(args.root_folder_path).resolve()
    calibre_library_path = Path(args.calibredb_path).resolve()

    # Validate Calibre library path
    if not calibre_library_path.exists():
        print(f"Error: Calibre library path '{calibre_library_path}' does not exist.")
        sys.exit(1)

    # Validate root folder path
    if not root_folder_path.exists() or not root_folder_path.is_dir():
        print(f"Error: Root folder '{root_folder_path}' is not a valid directory.")
        sys.exit(1)

    # Collect all .mobi files
    all_mobi_files = sorted(
        list(root_folder_path.rglob("*.mobi")), key=lambda x: natural_sort_key(x.name)
    )

    print(f"\nTotal .mobi files found: {len(all_mobi_files)}\n")

    if args.dry_run:
        print("** Dry Run Enabled: No books will be added to the Calibre library. **\n")
        for mobi_file in all_mobi_files:
            print(f"[DRY RUN] Would add: File='{mobi_file.name}'")
    else:
        success_count = 0
        failure_count = 0
        for mobi_file in all_mobi_files:
            print(f"Adding '{mobi_file.name}'...", end=" ")
            success, message = add_mobi_with_calibredb(calibre_library_path, mobi_file)
            if success:
                print("Success.")
                success_count += 1
            else:
                print(f"Failed.\n\tError: {message}")
                failure_count += 1

        print(f"\nSuccessfully added {success_count} .mobi file(s) to Calibre.")
        if failure_count > 0:
            print(f"Failed to add {failure_count} .mobi file(s). See errors above.")


if __name__ == "__main__":
    main()
