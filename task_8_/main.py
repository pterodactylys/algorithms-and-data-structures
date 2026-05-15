"""
Главное приложение - GUI для лабораторной работы 4
Исследование алгоритмов оптимизации полного перебора
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random
from pathfinding import PathFinder
from puzzle15 import Puzzle15Solver


class PathFindingTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.grid_size = 7
        self.cell_size = 60
        self.start = None
        self.end = None
        self.blocked = set()
        self.current_path = None
        self.path_finder = PathFinder(self.grid_size)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание элементов интерфейса"""
        # Топ-панель с кнопками
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Выберите алгоритм:").pack(side=tk.LEFT, padx=5)
        
        self.algo_var = tk.StringVar(value="backtrack")
        algorithms = [
            ("Простой перебор", "backtrack"),
            ("Эвристика Варнсдорфа", "warnsdorff"),
            ("Отсечение связности", "connectivity"),
            ("Backjumping", "backjumping"),
        ]
        
        for label, value in algorithms:
            ttk.Radiobutton(control_frame, text=label, variable=self.algo_var,
                          value=value).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Найти путь", 
                  command=self._solve).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить", 
                  command=self._clear).pack(side=tk.LEFT, padx=5)
        
        # Канвас для отрисовки сетки
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Label(canvas_frame, text="Левый клик: старт | Правый клик: финиш | Средний: блокировка").pack()
        ttk.Label(canvas_frame, text="Найденный путь: синяя линия и номера шагов").pack()
        
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.grid_size * self.cell_size,
                               height=self.grid_size * self.cell_size,
                               bg='white', borderwidth=2, relief=tk.SUNKEN)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Button-2>", self._on_middle_click)
        
        self._draw_grid()
        
        # Информационная панель
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="Статистика:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.info_text = tk.Text(info_frame, height=15, width=40, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def _draw_grid(self):
        """Отрисовка сетки"""
        self.canvas.delete("all")
        
        # Сетка
        for i in range(self.grid_size + 1):
            self.canvas.create_line(0, i * self.cell_size, 
                                   self.grid_size * self.cell_size, i * self.cell_size)
            self.canvas.create_line(i * self.cell_size, 0, 
                                   i * self.cell_size, self.grid_size * self.cell_size)
        
        # Заблокированные клетки
        for x, y in self.blocked:
            x1 = x * self.cell_size + 1
            y1 = y * self.cell_size + 1
            x2 = x1 + self.cell_size - 2
            y2 = y1 + self.cell_size - 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray', outline='gray')
        
        # Стартовая клетка (зеленая)
        if self.start:
            x, y = self.start
            x1 = x * self.cell_size + 1
            y1 = y * self.cell_size + 1
            x2 = x1 + self.cell_size - 2
            y2 = y1 + self.cell_size - 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='green', outline='green')
        
        # Финишная клетка (красная)
        if self.end:
            x, y = self.end
            x1 = x * self.cell_size + 1
            y1 = y * self.cell_size + 1
            x2 = x1 + self.cell_size - 2
            y2 = y1 + self.cell_size - 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='red')
        
        # Путь (линия + номера шагов)
        if self.current_path:
            for x, y in self.current_path:
                if (x, y) != self.start and (x, y) != self.end:
                    x1 = x * self.cell_size + 1
                    y1 = y * self.cell_size + 1
                    x2 = x1 + self.cell_size - 2
                    y2 = y1 + self.cell_size - 2
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='#b3d9ff', outline='#b3d9ff')

            path_points = []
            for x, y in self.current_path:
                path_points.extend([
                    x * self.cell_size + self.cell_size // 2,
                    y * self.cell_size + self.cell_size // 2,
                ])

            for index in range(len(self.current_path) - 1):
                x1, y1 = self.current_path[index]
                x2, y2 = self.current_path[index + 1]
                self.canvas.create_line(
                    x1 * self.cell_size + self.cell_size // 2,
                    y1 * self.cell_size + self.cell_size // 2,
                    x2 * self.cell_size + self.cell_size // 2,
                    y2 * self.cell_size + self.cell_size // 2,
                    fill='#0066cc',
                    width=4,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                )

            for index, (x, y) in enumerate(self.current_path, start=1):
                if (x, y) != self.start and (x, y) != self.end:
                    x1 = x * self.cell_size + 1
                    y1 = y * self.cell_size + 1
                    x2 = x1 + self.cell_size - 2
                    y2 = y1 + self.cell_size - 2
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                           text=str(index), font=('Arial', 9, 'bold'), fill='navy')

            if self.start:
                sx, sy = self.start
                self.canvas.create_text(sx * self.cell_size + self.cell_size // 2,
                                       sy * self.cell_size + self.cell_size // 2,
                                       text='S', font=('Arial', 10, 'bold'), fill='white')
            if self.end:
                ex, ey = self.end
                self.canvas.create_text(ex * self.cell_size + self.cell_size // 2,
                                       ey * self.cell_size + self.cell_size // 2,
                                       text='F', font=('Arial', 10, 'bold'), fill='white')
    
    def _on_left_click(self, event):
        """Установка стартовой клетки"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.start = (x, y)
            if self.start in self.blocked:
                self.blocked.remove(self.start)
            self._draw_grid()
    
    def _on_right_click(self, event):
        """Установка финишной клетки"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.end = (x, y)
            if self.end in self.blocked:
                self.blocked.remove(self.end)
            self._draw_grid()
    
    def _on_middle_click(self, event):
        """Блокировка/разблокировка клетки"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            cell = (x, y)
            if cell != self.start and cell != self.end:
                if cell in self.blocked:
                    self.blocked.remove(cell)
                else:
                    self.blocked.add(cell)
                self._draw_grid()
    
    def _solve(self):
        """Решение задачи выбранным алгоритмом"""
        if not self.start or not self.end:
            messagebox.showwarning("Ошибка", "Установите стартовую и финишную клетку!")
            return
        
        algo = self.algo_var.get()
        
        if algo == "backtrack":
            self.current_path = self.path_finder.backtrack_simple(self.start, self.end, self.blocked)
        elif algo == "warnsdorff":
            self.current_path = self.path_finder.warnsdorff_heuristic(self.start, self.end, self.blocked)
        elif algo == "connectivity":
            self.current_path = self.path_finder.connectivity_pruning(self.start, self.end, self.blocked)
        elif algo == "backjumping":
            self.current_path = self.path_finder.backjumping(self.start, self.end, self.blocked)
        
        self._draw_grid()
        self._update_info()
    
    def _update_info(self):
        """Обновление информационной панели"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        stats = self.path_finder.stats
        
        text = "Результат:\n"
        text += f"Найден: {'Да' if stats.get('found') else 'Нет'}\n"
        text += f"Длина пути: {stats.get('path_length', 0)}\n"
        text += f"Шагов: {stats.get('steps', 0)}\n"
        text += f"Время: {stats.get('time', 0):.4f} сек\n"
        
        if stats.get('found'):
            text += f"\nПусто: {self.grid_size * self.grid_size - len(self.blocked)} клеток\n"
        
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)
    
    def _clear(self):
        """Очистка поля"""
        self.start = None
        self.end = None
        self.blocked.clear()
        self.current_path = None
        self._draw_grid()
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)


class Puzzle15Tab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.size = 4
        self.cell_size = 80
        self.puzzle = Puzzle15Solver(self.size)
        self.current_state = tuple(range(1, self.size * self.size)) + (0,)
        self.current_path = None
        self.solution_path = None
        self.solution_step = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание элементов интерфейса"""
        # Топ-панель
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Выберите алгоритм:").pack(side=tk.LEFT, padx=5)
        
        self.algo_var = tk.StringVar(value="manhattan")
        algorithms = [
            ("Manhattan", "manhattan"),
            ("BFS", "bfs"),
            ("IDA*", "ida"),
            ("Backjumping", "backjumping"),
        ]
        
        for label, value in algorithms:
            ttk.Radiobutton(control_frame, text=label, variable=self.algo_var,
                          value=value).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Решить", 
                  command=self._solve).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Перемешать", 
                  command=self._shuffle).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сброс", 
                  command=self._reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="← Шаг", 
                  command=self._prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Шаг →", 
                  command=self._next_step).pack(side=tk.LEFT, padx=5)
        
        # Основной контент
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая часть - пазл
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(left_frame, text="Текущее состояние:", font=('Arial', 10, 'bold')).pack()
        
        self.canvas = tk.Canvas(left_frame,
                               width=self.size * self.cell_size,
                               height=self.size * self.cell_size,
                               bg='white', borderwidth=2, relief=tk.SUNKEN)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Правая часть - информация
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Статистика:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.info_text = tk.Text(right_frame, height=15, width=40, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self._draw_puzzle()
    
    def _draw_puzzle(self):
        """Отрисовка пазла"""
        self.canvas.delete("all")
        
        for i in range(self.size):
            for j in range(self.size):
                idx = i * self.size + j
                val = self.current_state[idx]
                
                x1 = j * self.cell_size + 1
                y1 = i * self.cell_size + 1
                x2 = x1 + self.cell_size - 2
                y2 = y1 + self.cell_size - 2
                
                if val == 0:
                    color = 'white'
                    text = ''
                else:
                    color = 'lightblue'
                    text = str(val)
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black', width=2)
                
                if text:
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                           text=text, font=('Arial', 16, 'bold'))

        if self.solution_path:
            self.canvas.create_text(
                self.size * self.cell_size // 2,
                12,
                text=f"Шаг {self.solution_step + 1}/{len(self.solution_path)}",
                font=('Arial', 10, 'bold'),
                fill='darkblue'
            )
    
    def _on_canvas_click(self, event):
        """Обработка клика для перемещения костяшек"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.size and 0 <= y < self.size:
            idx = y * self.size + x
            zero_idx = self.current_state.index(0)
            
            # Проверка соседства
            zero_row, zero_col = zero_idx // self.size, zero_idx % self.size
            if abs(zero_row - y) + abs(zero_col - x) == 1:
                state_list = list(self.current_state)
                state_list[idx], state_list[zero_idx] = state_list[zero_idx], state_list[idx]
                self.current_state = tuple(state_list)
                self._draw_puzzle()
    
    def _shuffle(self):
        """Перемешивание пазла"""
        state = list(self.puzzle.goal)
        for _ in range(100):
            neighbors = self.puzzle._get_neighbors(tuple(state))
            state = list(neighbors[random.randint(0, len(neighbors) - 1)])
        self.current_state = tuple(state)
        self.current_path = None
        self.solution_path = None
        self.solution_step = 0
        self._draw_puzzle()
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _reset(self):
        """Сброс на начальное состояние"""
        self.current_state = self.puzzle.goal
        self.current_path = None
        self.solution_path = None
        self.solution_step = 0
        self._draw_puzzle()
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _solve(self):
        """Решение пазла выбранным алгоритмом"""
        algo = self.algo_var.get()
        
        if algo == "manhattan":
            self.current_path = self.puzzle.manhattan_heuristic(self.current_state)
        elif algo == "bfs":
            self.current_path = self.puzzle.bfs_search(self.current_state)
        elif algo == "ida":
            self.current_path = self.puzzle.ida_star(self.current_state)
        elif algo == "backjumping":
            self.current_path = self.puzzle.backjumping_solver(self.current_state)

        self.solution_path = self.current_path
        self.solution_step = 0
        if self.solution_path:
            self.current_state = self.solution_path[0]
        self._draw_puzzle()
        
        self._update_info()

    def _show_step(self, step: int):
        """Показать конкретный шаг решения"""
        if not self.solution_path:
            return
        self.solution_step = max(0, min(step, len(self.solution_path) - 1))
        self.current_state = self.solution_path[self.solution_step]
        self._draw_puzzle()
        self._update_info()

    def _prev_step(self):
        """Предыдущий шаг решения"""
        self._show_step(self.solution_step - 1)

    def _next_step(self):
        """Следующий шаг решения"""
        self._show_step(self.solution_step + 1)
    
    def _update_info(self):
        """Обновление информационной панели"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        stats = self.puzzle.stats
        
        text = "Результат:\n"
        text += f"Найден: {'Да' if stats.get('found') else 'Нет'}\n"
        text += f"Шагов до решения: {stats.get('path_length', 0)}\n"
        text += f"Рассмотрено состояний: {stats.get('steps', 0)}\n"
        text += f"Время: {stats.get('time', 0):.4f} сек\n"
        
        if stats.get('found'):
            text += f"\nТекущий шаг просмотра: {self.solution_step + 1 if self.solution_path else 0}\n"
            text += f"Всего шагов в решении: {len(self.solution_path) if self.solution_path else 0}\n"
        
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 4 - Оптимизация перебора")
        self.root.geometry("1000x700")
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Поиск пути
        self.pathfinding_tab = PathFindingTab(self.notebook)
        self.notebook.add(self.pathfinding_tab.frame, text="Задача 1: Поиск пути")
        
        # Вкладка 2: 15-пазл
        self.puzzle_tab = Puzzle15Tab(self.notebook)
        self.notebook.add(self.puzzle_tab.frame, text="Задача 2: пятнашки")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
