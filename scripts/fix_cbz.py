import os
import zipfile
import shutil


def fix_cbz_structure(input_cbz_path, output_cbz_path, temp_dir="temp_cbz"):
    # Step 1: Extract the CBZ file
    with zipfile.ZipFile(input_cbz_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Step 2: Flatten the directory structure
    all_images = []
    for root, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                all_images.append(os.path.join(root, file))

    # Step 3: Sort images by file name (to maintain reading order)
    all_images.sort()

    # Step 4: Create a new flat folder for the fixed structure
    fixed_dir = os.path.join(temp_dir, "fixed")
    os.makedirs(fixed_dir, exist_ok=True)

    for i, img_path in enumerate(all_images):
        # Create sequential file names
        ext = os.path.splitext(img_path)[1]
        new_name = f"{i:04}{ext}"
        shutil.copy(img_path, os.path.join(fixed_dir, new_name))

    # Step 5: Create a new CBZ file
    with zipfile.ZipFile(output_cbz_path, "w") as zip_ref:
        for root, _, files in os.walk(fixed_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(
                    file_path, fixed_dir
                )  # Relative path inside the zip
                zip_ref.write(file_path, arcname)

    # Step 6: Clean up temporary files
    shutil.rmtree(temp_dir)
    print(f"Fixed CBZ file created at: {output_cbz_path}")


def process_cbz_in_folder(folder_path):
    # Get all .cbz files in the folder
    cbz_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".cbz")]

    for cbz_file in cbz_files:
        input_cbz_path = os.path.join(folder_path, cbz_file)
        output_cbz_path = os.path.join(
            folder_path, f"{os.path.splitext(cbz_file)[0]}_fixed.cbz"
        )

        print(f"Processing: {input_cbz_path}")
        fix_cbz_structure(input_cbz_path, output_cbz_path)
        print(f"Saved fixed CBZ: {output_cbz_path}")


# Folder containing the CBZ files
folder = "."  # Replace with the folder containing your CBZ files

# Run the processing function
process_cbz_in_folder(folder)
