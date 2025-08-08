import os
import shutil

def copy_folder_contents(src_folder, dst_folder):
    """
    Copy all contents (files + subfolders) from src_folder to dst_folder.
    Creates dst_folder if it does not exist.
    """
    # Ensure the destination folder exists
    os.makedirs(dst_folder, exist_ok=True)

    # Loop through all items in the source folder
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dst_path = os.path.join(dst_folder, item)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)

    print(f"Copied contents from '{src_folder}' to '{dst_folder}'.")

#  uncomment to test usage:

# copy_folder_contents("./uploads", "./learned_document")
