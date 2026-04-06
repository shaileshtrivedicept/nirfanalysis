import os
import shutil

def get_image_files(directory):
    """
    Retrieves all image files (jpg, jpeg, png) from a directory.
    """
    image_extensions = (".jpg", ".jpeg", ".png")
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(image_extensions)
    ]

def ensure_dir(directory):
    """
    Ensures a directory exists, creating it if necessary.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_processed_dir(directory):
    """
    Deletes all files in the processed data directory.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
