"""
Utilitaires pour optimiser les performances du file sorter
"""
import time
import logging
from functools import wraps


def timing_decorator(func):
    """Décorateur pour mesurer le temps d'exécution d'une fonction."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        logging.debug(
            (
                f"{func.__name__} executed in {execution_time:.3f} seconds"
            )
        )
        return result
    return wrapper


class PerformanceMonitor:
    """
    Moniteur de performance pour suivre les opérations de tri.
    """

    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'files_moved': 0,
            'total_time': 0,
            'last_operation_time': 0
        }

    def start_operation(self):
        """Démarre le chronométrage d'une opération."""
        self.start_time = time.time()

    def end_operation(self, files_processed=0, files_moved=0):
        """Termine le chronométrage et met à jour les statistiques."""
        if hasattr(self, 'start_time'):
            operation_time = time.time() - self.start_time
            self.stats['last_operation_time'] = operation_time
            self.stats['total_time'] += operation_time
            self.stats['files_processed'] += files_processed
            self.stats['files_moved'] += files_moved

    def get_performance_summary(self):
        """Retourne un résumé des performances."""
        if self.stats['files_processed'] == 0:
            return "No files processed yet."

        avg_time_per_file = self.stats['total_time'] / \
            self.stats['files_processed']
        move_rate = (self.stats['files_moved'] /
                     self.stats['files_processed']) * 100

        return (
            f"Performance Summary:\n"
            f"- Files processed: {self.stats['files_processed']}\n"
            f"- Files moved: {self.stats['files_moved']}\n"
            f"- Move rate: {move_rate:.1f}%\n"
            f"- Total time: {self.stats['total_time']:.3f}s\n"
            f"- Average time per file: {avg_time_per_file:.3f}s\n"
            f"- Last operation: {self.stats['last_operation_time']:.3f}s"
        )


def should_use_threading(num_files, file_sizes=None):
    """
    Détermine si le threading doit être utilisé selon le contexte.

    Args:
        num_files: Nombre de fichiers à traiter
        file_sizes: Liste optionnelle des tailles des fichiers en bytes

    Returns:
        tuple: (use_threading, recommended_workers)
    """

    # Règles de base
    if num_files <= 2:
        return False, 1

    if num_files <= 10:
        return True, 2

    if num_files <= 50:
        return True, 4

    # Pour de très gros batches, limiter le nombre de threads
    max_workers = min(8, max(2, num_files // 15))

    # Si on a des informations sur les tailles des fichiers
    if file_sizes:
        avg_size = sum(file_sizes) / len(file_sizes)
        # Pour de gros fichiers, réduire le parallélisme
        if avg_size > 100 * 1024 * 1024:  # > 100MB
            max_workers = min(max_workers, 2)

    return True, max_workers


def estimate_operation_time(num_files, avg_file_size_mb=1):
    """
    Estime le temps d'opération basé sur des heuristiques.

    Args:
        num_files: Nombre de fichiers
        avg_file_size_mb: Taille moyenne des fichiers en MB

    Returns:
        float: Temps estimé en secondes
    """
    # Temps de base par fichier (pattern matching, path resolution)
    base_time_per_file = 0.001  # 1ms par fichier

    # Temps de déplacement selon la taille
    move_time_per_mb = 0.01  # 10ms par MB

    total_time = (base_time_per_file * num_files) + \
        (move_time_per_mb * avg_file_size_mb * num_files)

    return total_time


# Instance globale du moniteur de performance
performance_monitor = PerformanceMonitor()
