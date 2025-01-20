# Manga Processing Utility Suite Documentation

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Scripts](#scripts)
    - [fix_cbz.py](#fix_cbzpy)
    - [import_to_calibre.py](#import_to_calibrepy)
    - [batch_combine_and_process_cbz.py](#batch_combine_and_process_cbzpy)
    - [combine_and_process_cbz.py](#combine_and_process_cbzpy)
    - [Other Scripts](#other-scripts)
- [Modules and Dependencies](#modules-and-dependencies)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)

## Overview

The **Manga Processing Utility Suite** is a collection of Python scripts designed to streamline the management, processing, and conversion of manga collections stored in CBZ (Comic Book Zip) format. This suite automates tasks such as fixing CBZ file structures, combining chapters, converting to MOBI format for e-readers, and importing the processed files into the Calibre library. By leveraging tools like Kindle Comic Converter (kcc) and Calibre's `calibredb`, this suite offers a comprehensive solution for manga enthusiasts and library managers.

## Features

- **CBZ Structure Fixing:** Ensures CBZ files have a flat and consistent directory structure for compatibility.
- **Batch Processing:** Handles multiple manga folders and CBZ files simultaneously.
- **Conversion to MOBI:** Transforms CBZ files into MOBI format, optimized for e-readers.
- **Calibre Integration:** Automatically imports converted MOBI files into the Calibre library.
- **Metadata Handling:** Fetches and utilizes manga metadata from external APIs (e.g., Jikan API).
- **Dry Run Mode:** Simulates operations without making actual changes, useful for testing.
- **Logging:** Detailed logs for monitoring processes and debugging.
- **Status Management:** Tracks processed files to prevent redundant operations.

## Prerequisites

- **Python:** Version 3.6 or higher.
- **External Tools:**
  - **Kindle Comic Converter (kcc):** For converting CBZ to MOBI.
  - **KindleGen:** Amazon's tool for generating Kindle-compatible files.
  - **Calibre:** E-book management software with `calibredb` for library operations.
- **Python Packages:**
  - `logging`
  - `pathlib`
  - `sys`
  - `argparse`
  - `subprocess`
  - Other standard libraries as used in the scripts.

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

     Download from [Amazon's KindleGen Page](https://www.amazon.com/gp/feature.html?docId=1000765211) and place `kindlegen.exe` in the root directory.

   - **Calibre:**

     Install Calibre from [Calibre's Official Website](https://calibre-ebook.com/download).

4. **Verify Installation:**

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

#### Other Scripts

- **`combine_cbz.py`:** (Assumed functionality based on name) Likely handles the combination of multiple CBZ files into a single CBZ pack. Ensure to review and document based on actual implementation.

- **`__init__.py` Files:** Initialize Python packages. Typically empty or contain package-level variables and imports.

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

## Modules and Dependencies

The suite relies on a modular architecture with reusable components located in the `src` directory. Below is an overview of each module:

- **`src.constants`**
  
  Defines constants used across scripts, such as `CHAPTERS_PER_PART` and `STATUS_FILE`.

- **`src.cbz_convertor`**
  
  Contains functions to convert CBZ files to MOBI format using external tools like kcc and KindleGen.

- **`src.extractor`**
  
  Handles extraction and saving of cover images from CBZ files.

- **`src.grouper`**
  
  Manages grouping of CBZ files into packs based on chapter numbers.

- **`src.manga_info`**
  
  Fetches manga metadata from external APIs (e.g., Jikan API) to enrich the processing.

- **`src.parser`**
  
  Parses manga names and chapter numbers from CBZ filenames to assist in organizing.

- **`src.search_test`**
  
  (Assumed functionality) Possibly contains utilities for searching or testing search functionalities.

- **`src.state_manager`**
  
  Manages loading, updating, and checking the processing status to track completed tasks.

- **`src.utils`**
  
  Provides utility functions for:
  
  - Checking dependencies (e.g., verifying kcc installation).
  - Cleaning up temporary files and images.
  - Creating output directories.
  - Generating chapter ranges.
  - Sorting CBZ files naturally.
  - Parsing command-line arguments.
  - Setting up logging configurations.

- **`__init__.py` Files**
  
  Initialize Python packages, allowing modules to be imported seamlessly.

**Note:** Ensure all modules in the `src` directory are correctly implemented and free of errors. The `__pycache__` directories contain compiled Python files and can be ignored in version control.

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

### Logging

Logging configurations are managed via the `setup_logging` function in `src.utils.py`. By default, logging is set to the `INFO` level, but can be adjusted for verbosity.

```python
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
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

## Error Handling

The suite incorporates robust error handling mechanisms to ensure smooth operations and provide informative feedback:

- **Missing Files or Directories:**
  
  Scripts check for the existence of required files and directories, logging errors and exiting gracefully if not found.

- **API Failures:**
  
  Failures in fetching manga metadata from APIs (e.g., Jikan API) are logged as errors, preventing incomplete processing.

- **Conversion Failures:**
  
  Errors during CBZ to MOBI conversion are captured and logged, allowing users to identify and address issues.

- **Interrupted Processes:**
  
  Keyboard interruptions (e.g., Ctrl+C) are caught, logging a warning and exiting without leaving residual temporary files.

- **General Exceptions:**
  
  Unexpected errors are caught and logged with detailed messages to assist in debugging.

**Example Error Messages:**

```
Error: Calibre library path 'C:/Invalid/Path' does not exist.
Error: Unable to determine manga name from CBZ files.
Failed to convert Part 2 to MOBI.
```

## Logging

Logging is a critical component of the suite, providing real-time feedback and historical records of processing activities.

### Logging Levels

- **INFO:**
  
  General information about processing steps and statuses.

- **DEBUG:**
  
  Detailed information useful for debugging (activated with verbose mode).

- **WARNING:**
  
  Notices about potential issues or interruptions.

- **ERROR:**
  
  Critical issues that prevent certain tasks from completing.

### Log Configuration

Logging is configured in `src/utils.py` and can be customized as needed. By default, logs are output to the console, but can be extended to write to log files if required.

```python
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
```

**Example Log Output:**

```
2025-01-20 10:00:00 - INFO - Scanning directory: C:/Manga/manga1
2025-01-20 10:00:01 - INFO - Possible manga name: 'One Piece'
2025-01-20 10:00:02 - ERROR - Failed to retrieve manga information from Jikan API.
2025-01-20 10:00:03 - WARNING - Script interrupted by user. Exiting...
```

## License

This project is licensed under the [MIT License](LICENSE).

---

*For any issues, feature requests, or contributions, please open an issue or submit a pull request on the project's [GitHub repository](https://github.com/yourusername/manga-processor).*

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository:**

   Click the "Fork" button on the repository's GitHub page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/yourusername/manga-processor.git
   cd manga-processor
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**

   Implement your feature or bug fix.

5. **Commit Your Changes:**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Submit a Pull Request:**

   Go to the original repository and create a pull request from your fork.

**Please ensure your code adheres to the project's coding standards and includes appropriate documentation and tests.**

## Support

If you encounter any issues or have questions about the Manga Processing Utility Suite, feel free to reach out:

- **GitHub Issues:** [Open an Issue](https://github.com/yourusername/manga-processor/issues)
- **Email:** <your.email@example.com>
- **Community Forums:** [Manga Processor Discussions](https://github.com/yourusername/manga-processor/discussions)

We strive to respond to all queries promptly and appreciate your feedback!
