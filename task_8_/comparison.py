"""
Утилиты для тестирования и сравнения алгоритмов
"""
import time
import json
from pathfinding import PathFinder
from puzzle15 import Puzzle15Solver
from typing import Dict, List, Tuple


class AlgorithmComparator:
    """Класс для сравнения эффективности алгоритмов"""
    
    @staticmethod
    def compare_pathfinding():
        """Сравнение алгоритмов поиска пути"""
        grid_size = 7
        start = (0, 0)
        end = (grid_size - 1, grid_size - 1)
        blocked = set()  # Без препятствий для честного сравнения
        
        pathfinder = PathFinder(grid_size)
        results = {}
        
        algorithms = {
            'backtrack_simple': pathfinder.backtrack_simple,
            'warnsdorff': pathfinder.warnsdorff_heuristic,
            'connectivity': pathfinder.connectivity_pruning,
            'backjumping': pathfinder.backjumping,
        }
        
        print("=" * 60)
        print("СРАВНЕНИЕ АЛГОРИТМОВ ПОИСКА ПУТИ")
        print("=" * 60)
        print(f"Размер сетки: {grid_size}x{grid_size}")
        print(f"Стартовая клетка: {start}")
        print(f"Финишная клетка: {end}")
        print(f"Препятствий: {len(blocked)}")
        print("-" * 60)
        
        for algo_name, algo_func in algorithms.items():
            print(f"\nТестирование: {algo_name}")
            
            result = algo_func(start, end, blocked)
            stats = pathfinder.stats
            
            results[algo_name] = stats
            
            print(f"  Найден путь: {stats['found']}")
            print(f"  Длина пути: {stats['path_length']}")
            print(f"  Рассмотрено шагов: {stats['steps']}")
            print(f"  Время выполнения: {stats['time']:.6f} сек")
            
            if stats['path_length'] > 0:
                print(f"  Эффективность: {stats['path_length'] / stats['steps']:.4f}")
        
        return results
    
    @staticmethod
    def compare_puzzle15():
        """Сравнение алгоритмов для 15-пазла"""
        # Начальное состояние - слегка перемешанное
        initial_state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)
        
        solver = Puzzle15Solver(4)
        results = {}
        
        algorithms = {
            'manhattan': solver.manhattan_heuristic,
            'bfs': solver.bfs_search,
            'ida': solver.ida_star,
            'backjumping': solver.backjumping_solver,
        }
        
        print("\n" + "=" * 60)
        print("СРАВНЕНИЕ АЛГОРИТМОВ ДЛЯ 15-ПАЗЛА")
        print("=" * 60)
        print(f"Начальное состояние: {initial_state}")
        print("-" * 60)
        
        for algo_name, algo_func in algorithms.items():
            print(f"\nТестирование: {algo_name}")
            
            try:
                result = algo_func(initial_state)
                stats = solver.stats
                
                results[algo_name] = stats
                
                print(f"  Найдено решение: {stats['found']}")
                print(f"  Длина решения: {stats['path_length']} ходов")
                print(f"  Рассмотрено состояний: {stats['steps']}")
                print(f"  Время выполнения: {stats['time']:.6f} сек")
                
                if stats['steps'] > 0:
                    print(f"  Эффективность: {stats['path_length'] / stats['steps']:.4f}")
            except Exception as e:
                print(f"  Ошибка: {str(e)}")
        
        return results
    
    @staticmethod
    def save_results(pathfinding_results: Dict, puzzle_results: Dict, filename: str = "results.json"):
        """Сохранение результатов в JSON"""
        data = {
            'pathfinding': pathfinding_results,
            'puzzle15': puzzle_results,
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nРезультаты сохранены в {filename}")


if __name__ == "__main__":
    comparator = AlgorithmComparator()
    
    # Сравнение алгоритмов поиска пути
    pathfinding_results = comparator.compare_pathfinding()
    
    # Сравнение алгоритмов для пазла
    puzzle_results = comparator.compare_puzzle15()
    
    # Сохранение результатов
    comparator.save_results(pathfinding_results, puzzle_results)
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
