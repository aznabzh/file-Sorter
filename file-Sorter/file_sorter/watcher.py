import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_sorter.sorter import sort_single_file
from file_sorter.utils import print_changes


class SorterHandler(FileSystemEventHandler):
    """
    Handler optimisé qui ne traite que les fichiers concernés par l'événement.
    Évite le rescanning complet du dossier.
    """

    def __init__(self, directory, rules, dry_run=False):
        self.directory = directory
        self.rules = rules
        self.dry_run = dry_run
        self.processed_files = set()  # Cache simple en mémoire

    def _should_ignore_event(self, event):
        """Filtre les événements à ignorer."""
        if event.is_directory:
            return True
        # Ignorer les événements sur nos propres dossiers de destination
        dest_folders = {rule['destination'] for rule in self.rules}
        for dest in dest_folders:
            if dest in event.src_path:
                return True

        return False

    def _process_file_event(self, file_path, event_type):
        """
        Traite un événement sur un fichier spécifique.
        Inclut un délai pour éviter les fichiers en cours de téléchargement.
        """
        if not os.path.exists(file_path):
            return

        # Petite pause pour les fichiers
        # qui pourraient être en cours de téléchargement
        if event_type == "created":
            time.sleep(0.5)  # Attendre 500ms pour éviter les fichiers partiels

            # Vérifier si le fichier existe toujours après la pause
            if not os.path.exists(file_path):
                return

        # Pour les renommages, on retire l'ancien nom du cache
        if event_type == "moved" and file_path in self.processed_files:
            self.processed_files.discard(file_path)

        # Trier le fichier
        changes = sort_single_file(file_path, self.rules, dry_run=self.dry_run)

        if changes:
            print_changes(changes, dry_run=self.dry_run)
            # Marquer comme traité
            self.processed_files.add(file_path)

    def on_created(self, event):
        """Fichier créé (nouveau téléchargement, copie, etc.)."""
        if self._should_ignore_event(event):
            return

        logging.info(
            f"🆕 New file detected: {os.path.basename(event.src_path)}")
        self._process_file_event(event.src_path, "created")

    def on_moved(self, event):
        """Fichier renommé ou déplacé."""
        if self._should_ignore_event(event):
            return

        logging.info(
            f"📝 File renamed: {os.path.basename(event.src_path)} → "
            f"{os.path.basename(event.dest_path)}"
        )
        # Traiter le nouveau nom/emplacement
        self._process_file_event(event.dest_path, "moved")

    def on_modified(self, event):
        """Fichier modifié."""
        if self._should_ignore_event(event):
            return

        # Éviter de retraiter un fichier déjà traité dans cette session
        if event.src_path not in self.processed_files:
            logging.info(
                f"✏️ File modified: {os.path.basename(event.src_path)}")
            self._process_file_event(event.src_path, "modified")


def watch_directory(directory, rules, dry_run=False, stop_event=None):
    """
    Lance la surveillance optimisée du dossier.
    Ne scanne que les fichiers concernés par les événements.
    """
    # Premier scan complet au démarrage supprimé
    # (fait dans le thread principal)

    event_handler = SorterHandler(directory, rules, dry_run)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    # mode = "DRY RUN" if dry_run else "ACTIVE"
    # logging.info(f"🔍 Watching {directory} for changes... [{mode} MODE]")
    # logging.info("Press Ctrl+C to stop watching.")
    try:
        while not (stop_event and stop_event.is_set()):
            time.sleep(0.5)  # Augmenté de 0.2 à 0.5 pour réduire la charge CPU
    except KeyboardInterrupt:
        logging.info("\n🛑 Stopping file watcher...")
        observer.stop()
    observer.join()
    logging.info("✅ File watcher stopped.")
    logging.info(f"🛑 Watcher thread for {directory} has exited.")
