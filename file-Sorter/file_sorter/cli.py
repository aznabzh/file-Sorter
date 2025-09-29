import argparse
import os
import logging
import threading
from file_sorter.sorter import sort_files_auto_optimized, sort_files
from file_sorter.config_handler import ConfigHandler
from file_sorter.watcher import watch_directory
from file_sorter.utils import print_changes
from file_sorter.performance import performance_monitor

# Interface utilisateur en ligne de commande (CLI)
# et gestion des commandes CLI pour le tri de fichiers


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description='File Sorter CLI'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.json',
        help='chemin vers le fichier de config'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='simule le tri sans l effectuer'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Mode de surveillance (en temps réel)'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=None,
        help=(
            'Nombre max de threads en parallèle'
        )
    )
    parser.add_argument(
        '--no-threading',
        action='store_true',
        help='desactiver le threading'
    )
    parser.add_argument(
        '--show-performance',
        action='store_true',
        help='afficher les stats de performance'
    )

    args = parser.parse_args()

    logging.info(f"Loading configuration from {args.config}")
    try:
        config_handler = ConfigHandler(args.config)
        folders = config_handler.folders
    except (FileNotFoundError, ValueError, KeyError) as e:
        logging.error(f"Configuration error: {e}")
        return

    stop_event = threading.Event()
    threads = []

    # ----------- SECTION: Initial scan and summary output -----------

    logging.info("🔄 Initial scan...")
    all_changes = []
    
    for folder in folders:
        directory = folder["directory"]
        rules = folder["rules"]
        exclude = folder.get("exclude", None)

        if not os.path.isdir(directory):
            logging.warning(f"Directory does not exist: {directory}")
            continue

        # Choisir la stratégie de tri selon les options
        if args.no_threading:
            # Mode séquentiel forcé
            changes = sort_files(
                directory, rules, dry_run=args.dry_run, 
                use_thread_pool=False, exclude=exclude
            )
        elif args.max_workers:
            # Nombre de workers spécifié
            changes = sort_files(
                directory,
                rules,
                dry_run=args.dry_run,
                use_thread_pool=True,
                max_workers=args.max_workers,
                exclude=exclude
            )
        else:
            # Mode auto-optimisé (par défaut)
            changes = sort_files_auto_optimized(
                directory,
                rules,
                dry_run=args.dry_run,
                exclude=exclude
            )
        
        if changes:
            all_changes.extend(changes)

    if all_changes:
        print_changes(all_changes, dry_run=args.dry_run)
    else:
        logging.info("⚪ No files to move.")
    
    # Afficher les statistiques de performance si demandé
    if args.show_performance:
        print("\n" + "="*50)
        print(performance_monitor.get_performance_summary())
        print("="*50)

    # ----------- SECTION: Watch mode -----------
    if args.watch:
        mode = "DRY RUN" if args.dry_run else "ACTIVE"
        logging.info(f"🔍 Watching all folders for changes... [{mode} MODE]")
        logging.info("Press Ctrl+C to stop watching.")

        def run_watcher(directory, rules):
            watch_directory(
                directory,
                rules,
                dry_run=args.dry_run,
                stop_event=stop_event
            )

        for folder in folders:
            directory = folder["directory"]
            rules = folder["rules"]

            if not os.path.isdir(directory):
                continue

            t = threading.Thread(
                target=run_watcher,
                args=(directory, rules),
                daemon=True
            )
            t.start()
            threads.append(t)

        try:
            while any(t.is_alive() for t in threads):
                for t in threads:
                    t.join(timeout=0.2)
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C detected, stopping all watchers...")
            stop_event.set()
            for t in threads:
                t.join(timeout=2)
                print(f"Thread for {t} has been joined.")


if __name__ == '__main__':
    main()
