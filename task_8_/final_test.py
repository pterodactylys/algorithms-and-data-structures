#!/usr/bin/env python3
"""
Финальное тестирование всех компонентов
"""
import sys
from pathfinding import PathFinder
from puzzle15 import Puzzle15Solver


def test_pathfinding():
    """Тест алгоритмов поиска пути"""
    print("\n" + "="*70)
    print("ТЕСТ 1: Поиск пути на сетке 7×7")
    print("="*70)
    
    pf = PathFinder(7)
    start, end = (0, 0), (6, 6)
    obstacles = {(3, 3), (3, 4)}
    
    tests = [
        ('Простой перебор', pf.backtrack_simple),
        ('Эвристика Варнсдорфа', pf.warnsdorff_heuristic),
        ('Отсечение по связности', pf.connectivity_pruning),
        ('Backjumping', pf.backjumping),
    ]
    
    results = []
    for name, algo in tests:
        pf.stats = {}
        result = algo(start, end, obstacles)
        stats = pf.stats
        success = result is not None
        results.append(success)
        
        status = '✓ PASS' if success else '✗ FAIL'
        print(f"\n{status}: {name}")
        if success:
            print(f"  Длина пути: {len(result)} клеток")
            print(f"  Рассмотрено: {stats.get('steps', 0)} клеток")
            print(f"  Время: {stats.get('time', 0):.4f}с")
        else:
            print(f"  Рассмотрено: {stats.get('steps', 0)} клеток (нет решения)")
            print(f"  Время: {stats.get('time', 0):.4f}с")
    
    return all(results)


def test_puzzle15():
    """Тест алгоритмов для 15-пазла"""
    print("\n" + "="*70)
    print("ТЕСТ 2: 15-пазл 4×4 (простой случай - 1 ход)")
    print("="*70)
    
    solver = Puzzle15Solver(4)
    initial = tuple(list(range(1, 15)) + [0, 15])
    
    tests = [
        ('Manhattan A*', solver.manhattan_heuristic),
        ('BFS', solver.bfs_search),
        ('IDA*', solver.ida_star),
        ('Backjumping', solver.backjumping_solver),
    ]
    
    results = []
    for name, algo in tests:
        solver.stats = {}
        result = algo(initial)
        stats = solver.stats
        success = result is not None
        results.append(success)
        
        status = '✓ PASS' if success else '✗ FAIL'
        print(f"\n{status}: {name}")
        if success:
            print(f"  Ходов: {len(result) - 1}")
            print(f"  Рассмотрено состояний: {stats.get('steps', 0)}")
            print(f"  Время: {stats.get('time', 0):.6f}с")
        else:
            print(f"  Не найдено решение")
    
    return all(results)


def main():
    """Главная функция тестирования"""
    print("\n" + "█"*70)
    print("█ ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ - Лабораторная работа 4")
    print("█"*70)
    
    try:
        test1_pass = test_pathfinding()
        test2_pass = test_puzzle15()
        
        print("\n" + "="*70)
        print("ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*70)
        print(f"✓ Тест поиска пути: {'ПРОЙДЕН' if test1_pass else 'НЕ ПРОЙДЕН'}")
        print(f"✓ Тест 15-пазла: {'ПРОЙДЕН' if test2_pass else 'НЕ ПРОЙДЕН'}")
        
        if test1_pass and test2_pass:
            print("\n✓ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
            print("█"*70)
            return 0
        else:
            print("\n✗ Некоторые тесты не пройдены")
            print("█"*70)
            return 1
            
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
