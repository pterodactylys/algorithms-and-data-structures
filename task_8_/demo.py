#!/usr/bin/env python3
"""
Демонстрация работы всех алгоритмов
"""
from pathfinding import PathFinder
from puzzle15 import Puzzle15Solver


def demo_pathfinding():
    """Демонстрация алгоритмов поиска пути"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: Поиск пути на сетке 7x7")
    print("="*60)
    
    pf = PathFinder(7)
    start, end = (0, 0), (6, 6)
    obstacles = {(3, 3), (3, 4)}  # Решаемая конфигурация
    
    algorithms = [
        ('Простой перебор', pf.backtrack_simple),
        ('Эвристика Варнсдорфа', pf.warnsdorff_heuristic),
        ('Отсечение по связности', pf.connectivity_pruning),
        ('Backjumping', pf.backjumping),
    ]
    
    for name, algo in algorithms:
        pf.stats = {}
        result = algo(start, end, obstacles)
        stats = pf.stats
        
        status = '✓' if result else '✗'
        print(f"\n{status} {name}:")
        print(f"   Найден: {result is not None}")
        if result:
            print(f"   Длина пути: {len(result)}")
        print(f"   Рассмотрено клеток: {stats.get('steps', 'N/A')}")
        print(f"   Время: {stats.get('time', 'N/A'):.4f}с")


def demo_puzzle15():
    """Демонстрация алгоритмов для 15-пазла"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ: 15-пазл 4x4")
    print("="*60)
    
    solver = Puzzle15Solver(4)
    # Простой случай: одна плитка на месте
    initial = tuple(list(range(1, 15)) + [0, 15])
    
    algorithms = [
        ('Manhattan A*', solver.manhattan_heuristic),
        ('BFS (поиск в ширину)', solver.bfs_search),
        ('IDA*', solver.ida_star),
        ('Backjumping', solver.backjumping_solver),
    ]
    
    print(f"\nНачальное состояние (пустая клетка в позиции 14): ")
    print(f"   {initial}")
    
    for name, algo in algorithms:
        solver.stats = {}
        result = algo(initial)
        stats = solver.stats
        
        status = '✓' if result else '✗'
        print(f"\n{status} {name}:")
        print(f"   Найдено: {result is not None}")
        if result:
            print(f"   Ходов: {len(result) - 1}")
        print(f"   Рассмотрено состояний: {stats.get('steps', 'N/A')}")
        print(f"   Время: {stats.get('time', 'N/A'):.4f}с")


if __name__ == '__main__':
    demo_pathfinding()
    demo_puzzle15()
    print("\n" + "="*60)
    print("Демонстрация завершена!")
    print("="*60 + "\n")
