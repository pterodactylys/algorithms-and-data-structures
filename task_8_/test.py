#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы алгоритмов
"""
from pathfinding import PathFinder
from puzzle15 import Puzzle15Solver


def test_pathfinding():
    """Тестирование алгоритмов поиска пути"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ АЛГОРИТМОВ ПОИСКА ПУТИ")
    print("=" * 70)
    
    grid_size = 7
    start = (0, 0)
    end = (6, 6)
    blocked = {(3, 3), (3, 4), (4, 3)}  # Немного препятствий
    
    pathfinder = PathFinder(grid_size)
    
    tests = [
        ("Простой перебор", pathfinder.backtrack_simple),
        ("Эвристика Варнсдорфа", pathfinder.warnsdorff_heuristic),
        ("Отсечение связности", pathfinder.connectivity_pruning),
        ("Backjumping", pathfinder.backjumping),
    ]
    
    print(f"Параметры теста:")
    print(f"  Размер сетки: {grid_size}x{grid_size}")
    print(f"  Стартовая позиция: {start}")
    print(f"  Финишная позиция: {end}")
    print(f"  Препятствия: {blocked}")
    print()
    
    for test_name, algorithm in tests:
        print(f"Тест: {test_name}")
        print("-" * 70)
        
        result = algorithm(start, end, blocked)
        stats = pathfinder.stats
        
        print(f"  Найден путь: {stats['found']}")
        print(f"  Длина пути: {stats['path_length']}")
        print(f"  Количество шагов: {stats['steps']}")
        print(f"  Время выполнения: {stats['time']:.6f} сек")
        
        if stats['found'] and result:
            print(f"  Путь: {' -> '.join(str(p) for p in result[:5])}...")
        
        print()


def test_puzzle15():
    """Тестирование алгоритмов для 15-пазла"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ АЛГОРИТМОВ ДЛЯ 15-ПАЗЛА")
    print("=" * 70)
    
    # Небольшое начальное возмущение
    initial_state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)
    
    solver = Puzzle15Solver(4)
    
    tests = [
        ("Manhattan (A*)", solver.manhattan_heuristic),
        ("BFS", solver.bfs_search),
        ("IDA*", solver.ida_star),
        ("Backjumping", solver.backjumping_solver),
    ]
    
    print(f"Начальное состояние: {initial_state}")
    print(f"Целевое состояние:   {solver.goal}")
    print()
    
    for test_name, algorithm in tests:
        print(f"Тест: {test_name}")
        print("-" * 70)
        
        try:
            result = algorithm(initial_state)
            stats = solver.stats
            
            print(f"  Найдено решение: {stats['found']}")
            print(f"  Количество ходов: {stats['path_length']}")
            print(f"  Рассмотрено состояний: {stats['steps']}")
            print(f"  Время выполнения: {stats['time']:.6f} сек")
            
            if stats['found'] and result:
                print(f"  Первые 3 шага решения:")
                for i, state in enumerate(result[:4]):
                    print(f"    Шаг {i}: {state[:4]}")
                    print(f"           {state[4:8]}")
                    print(f"           {state[8:12]}")
                    print(f"           {state[12:]}")
                    if i < 3:
                        print()
        except Exception as e:
            print(f"  Ошибка: {e}")
        
        print()


def test_specific_case():
    """Тестирование специфического сценария"""
    print("=" * 70)
    print("СПЕЦИАЛЬНЫЙ ТЕСТ: СРАВНЕНИЕ ЭФФЕКТИВНОСТИ")
    print("=" * 70)
    print()
    
    # Поиск пути на большей сетке с препятствиями
    grid_size = 7
    start = (0, 0)
    end = (6, 6)
    
    # Создаем "лабиринт"
    blocked = set()
    for i in range(3, 5):
        for j in range(2, 5):
            blocked.add((i, j))
    
    pathfinder = PathFinder(grid_size)
    
    print(f"Поиск пути в лабиринте:")
    print(f"  Размер: {grid_size}x{grid_size}")
    print(f"  Препятствия: {len(blocked)} клеток")
    print()
    
    # Тест быстрого алгоритма
    print("Быстрый алгоритм (Варнсдорф + отсечение):")
    result = pathfinder.warnsdorff_heuristic(start, end, blocked)
    stats = pathfinder.stats
    print(f"  Найден: {stats['found']}")
    print(f"  Шагов: {stats['steps']}, Длина: {stats['path_length']}, Время: {stats['time']:.6f}")
    
    print()
    
    # Тест надежного алгоритма
    print("Надежный алгоритм (Backjumping):")
    result = pathfinder.backjumping(start, end, blocked)
    stats = pathfinder.stats
    print(f"  Найден: {stats['found']}")
    print(f"  Шагов: {stats['steps']}, Длина: {stats['path_length']}, Время: {stats['time']:.6f}")


def main():
    """Главная функция"""
    try:
        test_pathfinding()
        test_puzzle15()
        test_specific_case()
        
        print("=" * 70)
        print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО")
        print("=" * 70)
    
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
