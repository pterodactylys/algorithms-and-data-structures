"""
Алгоритмы для 15-пазла с различными оптимизациями
"""
import time
import heapq
from typing import Tuple, List, Set, Optional, Dict
from collections import deque


class Puzzle15Solver:
    def __init__(self, size: int = 4):
        self.size = size
        self.goal = tuple(range(1, size * size)) + (0,)
        self.stats = {}
    
    def _state_to_tuple(self, state: List[int]) -> Tuple:
        """Конвертирует состояние в кортеж"""
        return tuple(state)
    
    def _tuple_to_list(self, state: Tuple) -> List[int]:
        """Конвертирует кортеж в список"""
        return list(state)
    
    def _find_zero(self, state: Tuple) -> int:
        """Находит позицию пустой клетки"""
        return state.index(0)
    
    def _get_neighbors(self, state: Tuple) -> List[Tuple]:
        """Получить соседние состояния"""
        neighbors = []
        zero_pos = self._find_zero(state)
        row, col = zero_pos // self.size, zero_pos % self.size
        
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_pos = new_row * self.size + new_col
                state_list = list(state)
                state_list[zero_pos], state_list[new_pos] = state_list[new_pos], state_list[zero_pos]
                neighbors.append(tuple(state_list))
        
        return neighbors
    
    def manhattan_distance(self, state: Tuple) -> int:
        """Вычисляет манхэттенское расстояние"""
        distance = 0
        for i, val in enumerate(state):
            if val != 0:
                goal_pos = val - 1
                current_row, current_col = i // self.size, i % self.size
                goal_row, goal_col = goal_pos // self.size, goal_pos % self.size
                distance += abs(current_row - goal_row) + abs(current_col - goal_col)
        return distance
    
    # === ЗАДАЧА 1: Базовый алгоритм - манхэттенское расстояние ===
    def manhattan_heuristic(self, initial_state: Tuple, max_steps: int = 50000) -> Optional[List[Tuple]]:
        """Решение с использованием манхэттенского расстояния (A*)"""
        start_time = time.time()
        steps = [0]
        
        open_set = []
        heapq.heappush(open_set, (self.manhattan_distance(initial_state), 0, initial_state))
        
        came_from = {initial_state: None}
        g_score = {initial_state: 0}
        visited = set()
        
        while open_set and steps[0] < max_steps:
            _, current_g, current_state = heapq.heappop(open_set)
            steps[0] += 1
            
            if current_state == self.goal:
                # Восстанавливаем путь
                path = []
                state = current_state
                while state is not None:
                    path.append(state)
                    state = came_from[state]
                path.reverse()
                
                self.stats = {
                    'time': time.time() - start_time,
                    'steps': steps[0],
                    'path_length': len(path) - 1,
                    'found': True
                }
                return path
            
            visited.add(current_state)
            
            for neighbor in self._get_neighbors(current_state):
                if neighbor not in visited:
                    tentative_g = current_g + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current_state
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + self.manhattan_distance(neighbor)
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': 0,
            'found': False
        }
        return None
    
    # === ЗАДАЧА 2: BFS (поиск в ширину) ===
    def bfs_search(self, initial_state: Tuple, max_steps: int = 50000) -> Optional[List[Tuple]]:
        """Поиск в ширину (BFS)"""
        start_time = time.time()
        steps = [0]
        
        queue = deque([initial_state])
        visited = {initial_state}
        parent = {initial_state: None}
        
        while queue and steps[0] < max_steps:
            current_state = queue.popleft()
            steps[0] += 1
            
            if current_state == self.goal:
                # Восстанавливаем путь
                path = []
                state = current_state
                while state is not None:
                    path.append(state)
                    state = parent[state]
                path.reverse()
                
                self.stats = {
                    'time': time.time() - start_time,
                    'steps': steps[0],
                    'path_length': len(path) - 1,
                    'found': True
                }
                return path
            
            for neighbor in self._get_neighbors(current_state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current_state
                    queue.append(neighbor)
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': 0,
            'found': False
        }
        return None
    
    # === ЗАДАЧА 3: IDA* (Iterative Deepening A*) ===
    def ida_star(self, initial_state: Tuple, max_depth: int = 100) -> Optional[List[Tuple]]:
        """Iterative Deepening A* - ограниченный поиск по глубине"""
        start_time = time.time()
        steps = [0]
        
        def search(state, g, threshold, path):
            steps[0] += 1
            f = g + self.manhattan_distance(state)
            
            if f > threshold:
                return f, None
            
            if state == self.goal:
                return 0, path + [state]
            
            if g >= max_depth:
                return float('inf'), None
            
            min_threshold = float('inf')
            
            for neighbor in self._get_neighbors(state):
                if neighbor not in set(path):
                    t, result_path = search(neighbor, g + 1, threshold, path + [state])
                    if result_path:
                        return 0, result_path
                    if t < min_threshold:
                        min_threshold = t
            
            return min_threshold, None
        
        threshold = self.manhattan_distance(initial_state)
        
        while threshold != float('inf'):
            t, path = search(initial_state, 0, threshold, [])
            if path:
                self.stats = {
                    'time': time.time() - start_time,
                    'steps': steps[0],
                    'path_length': len(path) - 1,
                    'found': True
                }
                return path
            threshold = t
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': 0,
            'found': False
        }
        return None
    
    # === ЗАДАЧА 4: Backjumping с ограничением глубины ===
    def backjumping_solver(self, initial_state: Tuple, max_depth: int = 50) -> Optional[List[Tuple]]:
        """Backjumping - интеллектуальный поиск с анализом конфликтов"""
        start_time = time.time()
        steps = [0]
        
        def dfs(state, depth, path, visited_in_path):
            steps[0] += 1
            
            if state == self.goal:
                return path + [state]
            
            if depth > max_depth:
                return None, {state}
            
            neighbors = [neighbor for neighbor in self._get_neighbors(state) if neighbor not in visited_in_path]
            neighbors.sort(key=self.manhattan_distance)

            if not neighbors:
                return None, {state}

            conflict_set = set()
            
            for neighbor in neighbors:
                result = dfs(neighbor, depth + 1, path + [state], visited_in_path | {neighbor})
                if isinstance(result, tuple):
                    child_path, child_conflicts = result
                else:
                    child_path, child_conflicts = result, set()

                if child_path:
                    return child_path

                if state not in child_conflicts:
                    return None, child_conflicts

                conflict_set |= (child_conflicts - {state})
            
            conflict_set.add(state)
            return None, conflict_set
        
        result = dfs(initial_state, 0, [], {initial_state})
        if isinstance(result, tuple):
            result, _ = result
        
        self.stats = {
            'time': time.time() - start_time,
            'steps': steps[0],
            'path_length': len(result) - 1 if result else 0,
            'found': result is not None
        }
        
        return result
