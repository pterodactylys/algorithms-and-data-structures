"""
Алгоритмы поиска пути на сетке с оптимизациями
"""
import time
from collections import deque
from typing import List, Tuple, Set, Optional


class PathFinder:
    def __init__(self, grid_size: int = 7):
        self.grid_size = grid_size
        self.visited = set()
        self.path = []
        self.stats = {}
        
    def reset(self):
        self.visited.clear()
        self.path = []
        self.stats = {}
    
    def _is_valid(self, x: int, y: int, blocked: Set[Tuple[int, int]]) -> bool:
        """Проверка валидности клетки"""
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size and (x, y) not in blocked
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Получить соседей (4-направленное движение)"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors
    
    # === ЗАДАЧА 1: Базовый алгоритм - простой перебор с возвратом ===
    def backtrack_simple(self, start: Tuple[int, int], end: Tuple[int, int], 
                        blocked: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Простой перебор с возвратом"""
        self.reset()
        start_time = time.time()
        steps = [0]  # Количество шагов
        
        def dfs(x, y, path, visited):
            steps[0] += 1
            
            if (x, y) == end:
                if len(visited) == self.grid_size * self.grid_size - len(blocked):
                    return path
                return None
            
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked):
                    visited.add((nx, ny))
                    result = dfs(nx, ny, path + [(nx, ny)], visited)
                    if result:
                        return result
                    visited.remove((nx, ny))
            
            return None
        
        visited = {start}
        result = dfs(start[0], start[1], [start], visited)
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': len(result) if result else 0,
            'found': result is not None
        }
        
        return result
    
    # === ЗАДАЧА 2: Эвристика Варнсдорфа ===
    def warnsdorff_heuristic(self, start: Tuple[int, int], end: Tuple[int, int],
                            blocked: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Эвристика Варнсдорфа - выбираем клетку с минимальным числом ходов"""
        self.reset()
        start_time = time.time()
        steps = [0]
        
        def count_onward_moves(x, y, visited, blocked):
            """Считаем количество возможных ходов из позиции"""
            count = 0
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked):
                    count += 1
            return count
        
        def dfs(x, y, path, visited):
            steps[0] += 1
            
            if (x, y) == end:
                if len(visited) == self.grid_size * self.grid_size - len(blocked):
                    return path
                return None
            
            # Получаем соседей и сортируем по эвристике Варнсдорфа
            neighbors = []
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked):
                    degree = count_onward_moves(nx, ny, visited | {(nx, ny)}, blocked)
                    neighbors.append((degree, nx, ny))
            
            # Сортируем по количеству возможных ходов (минимум первым)
            neighbors.sort()
            
            for _, nx, ny in neighbors:
                visited.add((nx, ny))
                result = dfs(nx, ny, path + [(nx, ny)], visited)
                if result:
                    return result
                visited.remove((nx, ny))
            
            return None
        
        visited = {start}
        result = dfs(start[0], start[1], [start], visited)
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': len(result) if result else 0,
            'found': result is not None
        }
        
        return result
    
    # === ЗАДАЧА 3: Отсечение по связности ===
    def connectivity_pruning(self, start: Tuple[int, int], end: Tuple[int, int],
                            blocked: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Отсечение по связности - избегаем изоляции клеток"""
        self.reset()
        start_time = time.time()
        steps = [0]
        
        def is_connected(x, y, visited, blocked):
            """Проверяем, все ли соседние свободные клетки связаны"""
            unvisited = set()
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if (i, j) not in visited and (i, j) not in blocked:
                        unvisited.add((i, j))
            
            if not unvisited:
                return True
            
            # BFS для проверки связности
            start_cell = next(iter(unvisited))
            queue = deque([start_cell])
            visited_cells = {start_cell}
            
            while queue:
                cx, cy = queue.popleft()
                for nx, ny in self._get_neighbors(cx, cy):
                    if (nx, ny) in unvisited and (nx, ny) not in visited_cells:
                        visited_cells.add((nx, ny))
                        queue.append((nx, ny))
            
            return len(visited_cells) == len(unvisited)
        
        def dfs(x, y, path, visited):
            steps[0] += 1
            
            if (x, y) == end:
                if len(visited) == self.grid_size * self.grid_size - len(blocked):
                    return path
                return None
            
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked):
                    visited.add((nx, ny))
                    
                    # Проверка связности перед рекурсией
                    if is_connected(x, y, visited, blocked):
                        result = dfs(nx, ny, path + [(nx, ny)], visited)
                        if result:
                            return result
                    
                    visited.remove((nx, ny))
            
            return None
        
        visited = {start}
        result = dfs(start[0], start[1], [start], visited)
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': len(result) if result else 0,
            'found': result is not None
        }
        
        return result
    
    # === ЗАДАЧА 4: Backjumping ===
    def backjumping(self, start: Tuple[int, int], end: Tuple[int, int],
                   blocked: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Backjumping - интеллектуальный возврат с анализом конфликтов"""
        self.reset()
        start_time = time.time()
        steps = [0]
        
        total_free = self.grid_size * self.grid_size - len(blocked)

        def count_onward_moves(x: int, y: int, visited: Set[Tuple[int, int]]) -> int:
            """Сколько продолжений доступно из клетки."""
            count = 0
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked):
                    count += 1
            return count
        
        def dfs(x, y, path, visited, constraint_set=None):
            steps[0] += 1
            
            if constraint_set is None:
                constraint_set = set()
            
            # Если достигли конца и посетили все свободные клетки
            if (x, y) == end and len(visited) == total_free:
                return path
            
            neighbors = [
                (nx, ny)
                for nx, ny in self._get_neighbors(x, y)
                if (nx, ny) not in visited and self._is_valid(nx, ny, blocked)
            ]
            neighbors.sort(key=lambda cell: count_onward_moves(cell[0], cell[1], visited | {cell}))
            
            # Если нет соседей и не достигли цель - конфликт
            if not neighbors:
                return None, {(x, y)}
            
            conflict_set = set()

            for nx, ny in neighbors:
                if (nx, ny) in constraint_set:
                    continue
                
                visited.add((nx, ny))
                result, child_conflicts = dfs(
                    nx,
                    ny,
                    path + [(nx, ny)],
                    visited,
                    constraint_set | {(x, y)},
                )
                
                if result:
                    return result, set()
                
                visited.remove((nx, ny))

                # Если текущая вершина не входит в конфликт, можно подняться выше.
                if (x, y) not in child_conflicts:
                    return None, child_conflicts

                conflict_set |= (child_conflicts - {(x, y)})
            
            conflict_set.add((x, y))
            return None, conflict_set
        
        visited = {start}
        result, _ = dfs(start[0], start[1], [start], visited)
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': len(result) if result else 0,
            'found': result is not None
        }
        
        return result
