# Manga Processing Utility Suite Documentation

## Overview

The **Manga Processing Utility Suite** is a collection of Python scripts designed to streamline the management, processing, and conversion of manga collections stored in CBZ (Comic Book Zip) format. This suite automates tasks such as fixing CBZ file structures, combining chapters, converting to MOBI format for e-readers, and importing the processed files into the Calibre library. By leveraging tools like Kindle Comic Converter (kcc) and Calibre's `calibredb`, this suite offers a comprehensive solution for manga enthusiasts and library managers.

## Features

- **CBZ Structure Fixing:** Ensures CBZ files have a flat and consistent directory structure for compatibility.
- **Batch Processing:** Handles multiple manga folders and CBZ files simultaneously.
- **Conversion to MOBI:** Transforms CBZ files into MOBI format, optimized for e-readers.
- **Calibre Integration:** Automatically imports converted MOBI files into the Calibre library.
- **Metadata Handling:** Fetches and utilizes manga metadata from external APIs (e.g., Jikan API).
- **Dry Run Mode:** Simulates operations without making actual changes, useful for testing.
- **Status Management:** Tracks processed files to prevent redundant operations.

## Prerequisites

- **Python:** Version 3.6 or higher.
- **External Tools:**
  - **Kindle Comic Converter (kcc):** For converting CBZ to MOBI.
  - **KindleGen:** Amazon's tool for generating Kindle-compatible files.
  - **Calibre:** E-book management software with `calibredb` for library operations.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/manga-processor.git
   cd manga-processor
   ```

2. **Install Python Dependencies:**

   Ensure you have Python 3.6 or higher installed. Install required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install External Tools:**

   - **Kindle Comic Converter (kcc):**

     Download from [KCC GitHub Repository](https://github.com/ciromattia/kcc) and place `kcc.exe` in the root directory.

   - **KindleGen:**
    On Windows and macOS, install Kindle Previewer and kindlegen will be autodetected from it.

    Kindle Previewer: <https://www.amazon.com/Kindle-Previewer/b?ie=UTF8&node=21381691011>
    kindlegen.exe in Windows is available in: %LOCALAPPDATA%\Amazon\Kindle Previewer 3\lib\fc\bin\kindlegen.exe

   - **Calibre:**

     Install Calibre from [Calibre's Official Website](https://calibre-ebook.com/download).
4. **Configure External Tools Paths:**

   Copy kcc.exe and kindlegen.exe to the bin directory.

5. **Verify Installation:**

   Ensure that `kcc.exe`, `kindlegen.exe`, and `calibredb` are accessible and properly installed.

## Usage

The suite consists of multiple scripts, each handling specific tasks. Below is an overview of each script and how to use them.

### Scripts

#### `fix_cbz.py`

**Description:**

Fixes the directory structure of CBZ files by flattening nested folders and renaming image files sequentially to maintain reading order.

**Functions:**

- `fix_cbz_structure(input_cbz_path, output_cbz_path, temp_dir="temp_cbz")`
- `process_cbz_in_folder(folder_path)`

**Usage:**

```bash
python scripts/fix_cbz.py [OPTIONS]
```

**Options:**

- **No Arguments:** Processes CBZ files in the current directory.
  
  ```bash
  python scripts/fix_cbz.py
  ```

- **Specify Folder:** Modify the `folder` variable within the script or extend the script to accept command-line arguments for folder paths.

**Example Output:**

```
Processing: ./manga1.cbz
Fixed CBZ file created at: ./manga1_fixed.cbz
Saved fixed CBZ: ./manga1_fixed.cbz
```

#### `import_to_calibre.py`

**Description:**

Imports MOBI files into the Calibre library using Calibre's `calibredb` command-line tool.

**Functions:**

- `add_mobi_with_calibredb(calibredb_path: str, mobi_file: Path)`
- `parse_arguments()`
- `main()`

**Usage:**

```bash
python scripts/import_to_calibre.py [OPTIONS] root_folder_path
```

**Arguments:**

- `root_folder_path` (required): Path to the folder containing `.mobi` files to be added.

**Options:**

- `--calibredb-path`: Path to the `calibredb` executable. Default is `"C:/Users/giomartinelli/Calibre Library"`.
- `--dry-run`: Simulate adding books without making any changes.

**Examples:**

1. **Standard Import:**

   ```bash
   python scripts/import_to_calibre.py "C:/Manga/MOBI_Files"
   ```

2. **Dry Run Mode:**

   ```bash
   python scripts/import_to_calibre.py "C:/Manga/MOBI_Files" --dry-run
   ```

**Example Output:**

```
Total .mobi files found: 10

Adding 'manga1_001-005.mobi'... Success.
Adding 'manga1_006-010.mobi'... Failed.
    Error: calibredb add failed due to...
...
Successfully added 9 .mobi file(s) to Calibre.
Failed to add 1 .mobi file(s). See errors above.
```

#### `batch_combine_and_process_cbz.py`

**Description:**

Processes all manga folders within a parent directory by combining CBZ files, converting them to MOBI, and updating the processing status.

**Functions:**

- `process_all_manga_folders(parent_dir: Path, dry_run: bool)`
- `parse_arguments()`
- `main()`

**Usage:**

```bash
python scripts/batch_combine_and_process_cbz.py [OPTIONS] root_folder_path
```

**Arguments:**

- `root_folder_path` (required): Path to the parent directory containing manga folders with CBZ files.

**Options:**

- `--dry-run`: Simulate processing without making any changes.

**Examples:**

1. **Standard Batch Processing:**

   ```bash
   python scripts/batch_combine_and_process_cbz.py "C:/Manga/Collections"
   ```

2. **Dry Run Mode:**

   ```bash
   python scripts/batch_combine_and_process_cbz.py "C:/Manga/Collections" --dry-run
   ```

**Example Output:**

```
Processing all folders in 'C:/Manga/Collections'...
Processing Part 1/5 with 20 chapters.
Combining CBZ files...
Converting to MOBI...
Successfully converted Part 1 to MOBI.
...
All manga folders have been processed.
```

#### `combine_and_process_cbz.py`

**Description:**

Handles the combination of CBZ files into packs based on the number of chapters per part, converts them to MOBI format, and manages the processing status.

**Functions:**

- `process_manga_folder(dir: Path, dry_run: bool)`
- `process_packs(...)`
- `main()`

**Usage:**

```bash
python scripts/combine_and_process_cbz.py [OPTIONS]
```

**Options:**

- `root_folder_path` (required): Path to the folder containing manga chapters in CBZ format.
- `--dry-run`: Simulate processing without making any changes.

**Examples:**

1. **Standard Processing:**

   ```bash
   python scripts/combine_and_process_cbz.py "C:/Manga/manga1"
   ```

2. **Dry Run Mode:**

   ```bash
   python scripts/combine_and_process_cbz.py "C:/Manga/manga1" --dry-run
   ```

**Example Output:**

```
----------------------------------------
Scanning directory: C:/Manga/manga1
Possible manga name: 'Naruto'
Loaded status from 'C:/Manga/manga1/status.json'.
Status: {...}
Processing Part 1/4 with 25 chapters.
Combining CBZ files...
Converting to MOBI...
All parts have been processed and converted successfully.
```

### Example Workflow

1. **Fix CBZ Structures:**

   Ensure all CBZ files have a consistent and flat directory structure.

   ```bash
   python scripts/fix_cbz.py "C:/Manga/manga1"
   ```

2. **Combine and Process CBZ Files:**

   Combine fixed CBZ files into packs and convert them to MOBI.

   ```bash
   python scripts/combine_and_process_cbz.py "C:/Manga/manga1"
   ```

3. **Import MOBI Files into Calibre:**

   Add the converted MOBI files to your Calibre library.

   ```bash
   python scripts/import_to_calibre.py "C:/Manga/manga1/MOBI_Files"
   ```

4. **Batch Process Multiple Manga Collections:**

   Process all manga folders within a parent directory.

   ```bash
   python scripts/batch_combine_and_process_cbz.py "C:/Manga/Collections"
   ```

## Configuration

### Constants

Defined in `src/constants.py`, these constants control various aspects of the processing:

- **`CHAPTERS_PER_PART`**
  
  Number of chapters to include in each CBZ pack. Adjust based on desired pack size.

  ```python
  CHAPTERS_PER_PART = 25
  ```

- **`STATUS_FILE`**
  
  Path to the JSON file used for tracking processed packs and conversion statuses.

  ```python
  STATUS_FILE = "status.json"
  ```

### External Tools Paths

Ensure that the paths to external tools like `kcc.exe`, `kindlegen.exe`, and `calibredb` are correctly specified in the scripts or passed as command-line arguments.

For example, in `import_to_calibre.py`:

```python
parser.add_argument(
    "--calibredb-path",
    type=str,
    default="C:/Users/giomartinelli/Calibre Library",
    help="Path to the calibredb executable. Default: calibredb",
)
```

Adjust these paths based on your system's configuration.

## License

This project is licensed under the [MIT License](LICENSE).

---

*For any issues, feature requests, or contributions, please open an issue or submit a pull request on the project's [GitHub repository](https://github.com/yourusername/manga-processor).*
