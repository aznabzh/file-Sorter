import os
import shutil


def move_file(src, dest):
    """Move a file from src to dest. If dest exists, rename the file."""
    if not os.path.exists(src):
        raise FileNotFoundError(
            f"The source file {src} does not exist."
        )

    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    if not os.path.exists(dest):
        shutil.move(src, dest)
    else:
        base, extension = os.path.splitext(dest)
        counter = 1
        new_dest = f"{base}_{counter}{extension}"
        while os.path.exists(new_dest):
            counter += 1
            new_dest = f"{base}_{counter}{extension}"
        shutil.move(src, new_dest)


def create_directory(path):
    """Create a directory if it does not exist."""
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def get_files_in_directory(directory, extensions=None):
    """
    Get a list of files in the specified directory,
    optionally filtered by extensions.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(
            f"The path {directory} is not a directory."
        )

    files = []
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            if (
                extensions is None or
                any(entry.lower().endswith(ext.lower()) 
                    for ext in extensions)
            ):
                files.append(full_path)
    return files


def file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)
