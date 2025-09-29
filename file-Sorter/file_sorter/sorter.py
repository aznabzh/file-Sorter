import os
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from file_sorter.file_utils import move_file
from file_sorter.performance import timing_decorator, performance_monitor


@timing_decorator
def sort_files(
    source_dir,
    rules,
    dry_run=False,
    use_thread_pool=True,
    max_workers=4,
    exclude=None
):
    """
    Sort files in the source directory based on the provided rules.
    Returns a list of (src, dest) tuples for each file moved.

    Args:
        source_dir: Directory to sort
        rules: List of sorting rules
        dry_run: If True, only simulate the moves
        use_thread_pool: If True, use threading for parallel file moves
        max_workers: Maximum number of threads for parallel processing
    """
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(
            f"The directory {source_dir} does not exist."
        )

    files = [f for f in os.listdir(source_dir)
             if os.path.isfile(os.path.join(source_dir, f))]

    # Exclude files if needed
    if exclude:
        files = [
            f for f in files
            if not any(
                f.lower().endswith(ext.lower())
                for ext in exclude
            )
        ]

    # Phase 1: Batch preparation - Collect all moves to make
    moves_to_make = []

    for filename in files:
        file_path = os.path.join(source_dir, filename)

        for rule in rules:
            extensions = rule.get('extensions', [])
            pattern = rule.get('filename_pattern')
            destination = rule['destination']

            # Check if file extension matches
            if extensions and not any(
                filename.lower().endswith(ext.lower())
                for ext in extensions
            ):
                continue

            # Check pattern if specified (priority over extension alone)
            if pattern:
                if not re.search(pattern, filename):
                    continue
            elif not extensions:
                continue

            # Create destination path
            dest_dir = os.path.join(source_dir, destination)
            dest_path = os.path.join(dest_dir, filename)

            moves_to_make.append((file_path, dest_path, dest_dir))
            break  # Stop at first matching rule

    # Phase 2: Execute moves (batched)
    changes = []

    if not moves_to_make:
        return changes

    # Démarrer le monitoring des performances
    performance_monitor.start_operation()
    num_files = len(moves_to_make)

    if dry_run:
        # In dry run, just log what would be done
        for file_path, dest_path, _ in moves_to_make:
            logging.info(f"[DRY RUN] Would move {file_path} -> {dest_path}")
            changes.append((file_path, dest_path))

        performance_monitor.end_operation(
            files_processed=num_files, files_moved=0)
        return changes

    # Decide whether to use thread pool based on number of files
    if use_thread_pool and len(moves_to_make) > 3:
        changes = _batch_move_files_threaded(moves_to_make, max_workers)
    else:
        changes = _batch_move_files_sequential(moves_to_make)

    # Terminer le monitoring des performances
    performance_monitor.end_operation(
        files_processed=num_files,
        files_moved=len(changes)
    )

    return changes


def _batch_move_files_sequential(moves_to_make):
    """Execute file moves sequentially."""
    changes = []

    for file_path, dest_path, dest_dir in moves_to_make:
        try:
            # Create destination directory if it doesn't exist
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            move_file(file_path, dest_path)
            logging.info(f"Moved {file_path} -> {dest_path}")
            changes.append((file_path, dest_path))

        except Exception as e:
            logging.error(f"Failed to move {file_path}: {e}")

    return changes


def _batch_move_files_threaded(moves_to_make, max_workers):
    """Execute file moves using a thread pool for better performance."""
    changes = []

    def move_single_file(file_info):
        """Move a single file - thread-safe function."""
        file_path, dest_path, dest_dir = file_info
        try:
            # Create destination directory if it doesn't exist
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            move_file(file_path, dest_path)
            logging.info(f"Moved {file_path} -> {dest_path}")
            return (file_path, dest_path)

        except Exception as e:
            logging.error(f"Failed to move {file_path}: {e}")
            return None

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all move tasks
        future_to_move = {
            executor.submit(move_single_file, move_info): move_info
            for move_info in moves_to_make
        }

        # Collect results as they complete
        for future in as_completed(future_to_move):
            result = future.result()
            if result:
                changes.append(result)

    return changes


def sort_single_file(file_path, rules, dry_run=False, exclude=None):
    """
    Trie un seul fichier selon les règles.
    Optimisé pour traiter uniquement le fichier concerné par un événement.
    """
    if not os.path.isfile(file_path):
        return []

    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    changes = []

    # Exclude files if needed
    if exclude and any(
        filename.lower().endswith(ext.lower())
        for ext in exclude
    ):
        return changes

    # Ignorer les fichiers temporaires ou en cours de téléchargement
    if (filename.startswith('.') or
            filename.endswith('.tmp') or
            filename.endswith('.crdownload') or
            filename.endswith('.part')):
        return changes

    for rule in rules:
        extensions = rule.get('extensions', [])
        pattern = rule.get('filename_pattern')
        destination = rule['destination']

        # Check if file extension matches
        if extensions and not any(
            filename.lower().endswith(ext.lower())
            for ext in extensions
        ):
            continue

        # Check pattern if specified
        if pattern and not re.search(pattern, filename):
            continue
        elif not extensions and not pattern:
            continue

        dest_dir = os.path.join(directory, destination)
        dest_path = os.path.join(dest_dir, filename)

        if dry_run:
            logging.info(f"[DRY RUN] Would move {file_path} -> {dest_path}")
            changes.append((file_path, dest_path))
        else:
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            move_file(file_path, dest_path)
            logging.info(f"Moved {file_path} -> {dest_path}")
            changes.append((file_path, dest_path))

        break  # Stop at first matching rule

    return changes


def get_optimal_workers(num_files):
    """
    Détermine le nombre optimal de workers selon le nombre de fichiers.
    Évite la surcharge avec trop de threads pour peu de fichiers.
    """
    if num_files <= 3:
        return 1  # Séquentiel pour peu de fichiers
    elif num_files <= 10:
        return 2  # 2 threads pour batches moyens
    elif num_files <= 50:
        return 4  # 4 threads pour gros batches
    else:
        # Max 8 threads, ou 1 thread pour 10 fichiers
        return min(8, num_files // 10)


def sort_files_auto_optimized(source_dir, rules, dry_run=False, exclude=None):
    """
    Version auto-optimisée de sort_files qui choisit automatiquement
    la meilleure stratégie (séquentiel vs thread pool) selon le contexte.
    """
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(f"The directory {source_dir} does not exist.")

    files = [f for f in os.listdir(source_dir)
             if os.path.isfile(os.path.join(source_dir, f))]

    num_files = len(files)
    optimal_workers = get_optimal_workers(num_files)
    use_threading = optimal_workers > 1

    logging.debug(
        f"Processing {num_files} files with {optimal_workers} worker(s)")

    return sort_files(
        source_dir,
        rules,
        dry_run=dry_run,
        use_thread_pool=use_threading,
        max_workers=optimal_workers,
        exclude=exclude
    )
