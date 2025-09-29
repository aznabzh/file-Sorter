#!/usr/bin/env python3
"""
Script de test des optimisations de performance du file sorter.
"""
import os
import time
import tempfile
import shutil
import json
from pathlib import Path

from file_sorter.sorter import sort_files, sort_files_auto_optimized
from file_sorter.performance import performance_monitor


def create_test_files(directory, count=20):
    """Crée des fichiers de test dans le répertoire spécifié."""
    test_files = []
    
    extensions = ['.txt', '.pdf', '.jpg', '.png', '.doc', '.mp3', '.mp4']
    
    for i in range(count):
        ext = extensions[i % len(extensions)]
        filename = f"test_file_{i:03d}{ext}"
        filepath = Path(directory) / filename
        
        # Créer un fichier avec du contenu
        with open(filepath, 'w') as f:
            f.write(f"Test content for file {i}\n" * 10)
        
        test_files.append(str(filepath))
    
    return test_files


def create_test_config():
    """Crée une configuration de test."""
    return [
        {
            "extensions": [".txt", ".doc"],
            "destination": "documents"
        },
        {
            "extensions": [".jpg", ".png", ".gif"],
            "destination": "images"
        },
        {
            "extensions": [".mp3", ".mp4", ".avi"],
            "destination": "media"
        },
        {
            "extensions": [".pdf"],
            "destination": "pdfs"
        }
    ]


def benchmark_sorting_method(sort_func, directory, rules, method_name, **kwargs):
    """Benchmark une méthode de tri."""
    print(f"\n--- Testing {method_name} ---")
    
    start_time = time.time()
    changes = sort_func(directory, rules, **kwargs)
    end_time = time.time()
    
    execution_time = end_time - start_time
    files_moved = len(changes)
    
    print(f"Files moved: {files_moved}")
    print(f"Execution time: {execution_time:.3f} seconds")
    
    if files_moved > 0:
        print(f"Average time per file: {execution_time/files_moved:.3f} seconds")
    
    return {
        'method': method_name,
        'files_moved': files_moved,
        'execution_time': execution_time,
        'files_per_second': files_moved / execution_time if execution_time > 0 else 0
    }


def run_performance_test():
    """Lance un test complet de performance."""
    print("🧪 File Sorter Performance Test")
    print("=" * 50)
    
    # Créer un répertoire temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Test directory: {temp_dir}")
        
        # Créer les fichiers de test
        test_files = create_test_files(temp_dir, 30)
        print(f"Created {len(test_files)} test files")
        
        # Configuration de test
        rules = create_test_config()
        
        results = []
        
        # Test 1: Mode séquentiel
        test_files = create_test_files(temp_dir, 30)  # Recréer les fichiers
        result1 = benchmark_sorting_method(
            sort_files, temp_dir, rules, "Sequential Mode",
            use_thread_pool=False
        )
        results.append(result1)
        
        # Test 2: Mode thread pool (2 workers)
        test_files = create_test_files(temp_dir, 30)
        result2 = benchmark_sorting_method(
            sort_files, temp_dir, rules, "Thread Pool (2 workers)",
            use_thread_pool=True, max_workers=2
        )
        results.append(result2)
        
        # Test 3: Mode thread pool (4 workers)
        test_files = create_test_files(temp_dir, 30)
        result3 = benchmark_sorting_method(
            sort_files, temp_dir, rules, "Thread Pool (4 workers)",
            use_thread_pool=True, max_workers=4
        )
        results.append(result3)
        
        # Test 4: Mode auto-optimisé
        test_files = create_test_files(temp_dir, 30)
        result4 = benchmark_sorting_method(
            sort_files_auto_optimized, temp_dir, rules, "Auto-Optimized Mode"
        )
        results.append(result4)
        
        # Afficher le résumé
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 50)
        
        for result in results:
            print(f"{result['method']:25} | "
                  f"{result['files_moved']:3d} files | "
                  f"{result['execution_time']:6.3f}s | "
                  f"{result['files_per_second']:6.1f} files/s")
        
        # Identifier le plus rapide
        fastest = max(results, key=lambda x: x['files_per_second'])
        print(f"\n🏆 Fastest method: {fastest['method']} "
              f"({fastest['files_per_second']:.1f} files/s)")
        
        # Statistiques du moniteur de performance
        print("\n" + performance_monitor.get_performance_summary())


def test_file_count_scaling():
    """Test la scalabilité selon le nombre de fichiers."""
    print("\n🔬 File Count Scaling Test")
    print("=" * 50)
    
    file_counts = [5, 10, 20, 50, 100]
    rules = create_test_config()
    
    for count in file_counts:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_files = create_test_files(temp_dir, count)
            
            print(f"\nTesting with {count} files:")
            
            # Test séquentiel
            start = time.time()
            changes = sort_files(temp_dir, rules, use_thread_pool=False)
            seq_time = time.time() - start
            
            # Recréer les fichiers
            test_files = create_test_files(temp_dir, count)
            
            # Test avec threads
            start = time.time()
            changes = sort_files_auto_optimized(temp_dir, rules)
            thread_time = time.time() - start
            
            # Calculer l'amélioration
            improvement = ((seq_time - thread_time) / seq_time) * 100
            
            print(f"  Sequential: {seq_time:.3f}s")
            print(f"  Threaded:   {thread_time:.3f}s")
            print(f"  Improvement: {improvement:+.1f}%")


if __name__ == "__main__":
    try:
        run_performance_test()
        test_file_count_scaling()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
