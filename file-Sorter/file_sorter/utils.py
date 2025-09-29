import os
import logging


def print_changes(changes, dry_run=False):
    """Affiche un résumé des changements effectués."""
    if changes:
        action = "would be moved" if dry_run else "moved"
        logging.info(f"\n✅ {len(changes)} file(s) {action}:")
        for src, dest in changes:
            src_name = os.path.basename(src)
            dest_folder = os.path.basename(os.path.dirname(dest))
            logging.info(f"  📁 {src_name} → {dest_folder}/")
    else:
        logging.info("\n⚪ No files to move.")