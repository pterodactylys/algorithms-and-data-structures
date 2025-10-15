import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
import threading
from src import depersonalization as dp

class DepersonalizationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Система обезличивания медицинских данных")
        self.root.geometry("900x700")
        
        self.df = None
        self.original_df = None
        self.input_file = None
        self.output_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Загрузить файл", command=self.load_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Рассчитать k-anonymity", command=self.calculate_k_anonymity).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Обезличить", command=self.depersonalize).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Сохранить датасет", command=self.save_dataset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Выход", command=self.root.quit).pack(side=tk.RIGHT)
        
        # Левая панель - выбор квази-идентификаторов
        left_frame = ttk.LabelFrame(main_frame, text="Выберите квази идентификаторы", padding="5")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Список чекбоксов для квази-идентификаторов
        self.quasi_vars = {}
        self.quasi_checkboxes = []
        
        # Медицинские колонки (реальные из датасета поликлиники)
        medical_columns = [
            "Фамилия", "Имя", "Отчество", "Паспортные данные", 
            "СНИЛС", "Дата посещения врача", "Симптомы", "Анализы", 
            "Врач", "Дата готовности анализов", "Стоимость анализов", "Карта оплаты"
        ]
        
        for col in medical_columns:
            var = tk.BooleanVar()
            # Устанавливаем по умолчанию выбранными основные квази-идентификаторы
            if col in ["Паспортные данные", "Симптомы", "Дата посещения врача", "Стоимость анализов"]:
                var.set(True)
            
            self.quasi_vars[col] = var
            cb = ttk.Checkbutton(left_frame, text=col, variable=var)
            cb.pack(anchor=tk.W, pady=2)
            self.quasi_checkboxes.append(cb)
        
        # Правая панель - результаты k-anonymity
        right_frame = ttk.LabelFrame(main_frame, text="Топ плохих k anonymity", padding="5")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Список для отображения результатов
        self.results_listbox = tk.Listbox(right_frame, height=15, font=("Courier", 11))
        self.results_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=scrollbar.set)
        
        # Нижняя панель - файлы
        files_frame = ttk.Frame(main_frame)
        files_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        files_frame.columnconfigure(1, weight=1)
        files_frame.columnconfigure(3, weight=1)
        
        ttk.Label(files_frame, text="Имя файла ввода:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.input_label = ttk.Label(files_frame, text="Dataset", relief=tk.SUNKEN, padding="2")
        self.input_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        ttk.Label(files_frame, text="Имя файла вывода:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.output_label = ttk.Label(files_frame, text="Depersonalization", relief=tk.SUNKEN, padding="2")
        self.output_label.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Загрузите файл медицинских данных.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл медицинских данных",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("Загрузка медицинских данных...")
                self.root.update()
                
                self.df = pd.read_excel(file_path)
                self.original_df = self.df.copy()
                self.input_file = file_path
                
                # Обновляем список колонок на основе реальных данных
                self.update_column_checkboxes()
                
                # Обновляем имя входного файла
                filename = Path(file_path).name
                self.input_label.config(text=filename)
                
                self.status_var.set(f"Загружено {len(self.df)} записей пациентов из {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
                self.status_var.set("Ошибка загрузки файла")
    
    def update_column_checkboxes(self):
        """Обновляет список чекбоксов на основе колонок загруженного медицинского файла"""
        if self.df is None:
            return
        
        # Очищаем старые чекбоксы
        for cb in self.quasi_checkboxes:
            cb.destroy()
        
        self.quasi_checkboxes.clear()
        self.quasi_vars.clear()
        
        # Получаем фрейм для чекбоксов
        left_frame = None
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.LabelFrame) and "квази" in child.cget("text").lower():
                    left_frame = child
                    break
            if left_frame:
                break
        
        # Основные квази-идентификаторы для медицинских данных
        important_quasi_ids = ["Паспортные данные", "Симптомы", "Дата посещения врача", "Стоимость анализов"]
        
        # Создаем новые чекбоксы для колонок из файла
        for col in self.df.columns:
            var = tk.BooleanVar()
            
            # Автоматически выбираем основные квази-идентификаторы
            if col in important_quasi_ids:
                var.set(True)
            
            self.quasi_vars[col] = var
            cb = ttk.Checkbutton(left_frame, text=col, variable=var)
            cb.pack(anchor=tk.W, pady=2)
            self.quasi_checkboxes.append(cb)
    
    def get_selected_quasi_identifiers(self):
        """Возвращает список выбранных квази-идентификаторов"""
        selected = []
        for col, var in self.quasi_vars.items():
            if var.get() and col in self.df.columns:
                selected.append(col)
        return selected
    
    def calculate_k_anonymity(self):
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл медицинских данных")
            return
        
        selected_cols = self.get_selected_quasi_identifiers()
        if not selected_cols:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один квази-идентификатор")
            return
        
        try:
            self.status_var.set("Расчет k-anonymity медицинских данных...")
            self.root.update()
            
            # Очищаем список результатов
            self.results_listbox.delete(0, tk.END)
            
            # Рассчитываем топ плохих k-anonymity
            top_bad = dp.top_bad_k_anonymities(self.df, selected_cols, 5)
            
            # Отображаем результаты в формате: "1.12 (0.0012)"
            for i, (k_value, percentage) in enumerate(top_bad, 1):
                result_text = f"{i}.{k_value} ({percentage:.4f})"
                self.results_listbox.insert(tk.END, result_text)
            
            # Если результатов меньше 5, добавляем пустые строки
            while self.results_listbox.size() < 5:
                self.results_listbox.insert(tk.END, "")
            
            # Общая k-anonymity
            k_analysis = dp.calculate_k_anonymity(self.df, selected_cols)
            overall_k = k_analysis["k_anonymity"]
            
            self.status_var.set(f"K-anonymity рассчитана. Общее значение: {overall_k}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете k-anonymity: {str(e)}")
            self.status_var.set("Ошибка расчета k-anonymity")
    
    def depersonalize(self):
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл медицинских данных")
            return
        
        # Создаем окно выбора методов обезличивания
        self.show_depersonalization_options()
    
    def show_depersonalization_options(self):
        """Показывает окно с опциями обезличивания медицинских данных"""
        options_window = tk.Toplevel(self.root)
        options_window.title("Методы обезличивания медицинских данных")
        options_window.geometry("450x600")
        options_window.transient(self.root)
        options_window.grab_set()
        
        # Переменные для методов
        methods = {}
        
        ttk.Label(options_window, text="Выберите методы обезличивания:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Подавление (удаление идентифицирующих колонок)
        suppression_frame = ttk.LabelFrame(options_window, text="Подавление", padding="10")
        suppression_frame.pack(fill=tk.X, padx=20, pady=5)
        
        methods['suppress_names'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(suppression_frame, text="Удалить ФИО (Имя, Отчество)", 
                       variable=methods['suppress_names']).pack(anchor=tk.W)
        
        methods['suppress_docs'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(suppression_frame, text="Удалить документы (СНИЛС)", 
                       variable=methods['suppress_docs']).pack(anchor=tk.W)
        
        methods['suppress_medical'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(suppression_frame, text="Удалить детали (Анализы, Врач, Дата готовности)", 
                       variable=methods['suppress_medical']).pack(anchor=tk.W)
        
        # Обобщение
        generalization_frame = ttk.LabelFrame(options_window, text="Обобщение", padding="10")
        generalization_frame.pack(fill=tk.X, padx=20, pady=5)
        
        methods['generalize_passport'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(generalization_frame, text="Обобщить паспортные данные", 
                       variable=methods['generalize_passport']).pack(anchor=tk.W)
        
        methods['generalize_symptoms'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(generalization_frame, text="Обобщить симптомы до систем органов", 
                       variable=methods['generalize_symptoms']).pack(anchor=tk.W)
        
        methods['generalize_costs'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(generalization_frame, text="Обобщить стоимость анализов по квантилям", 
                       variable=methods['generalize_costs']).pack(anchor=tk.W)
        
        methods['generalize_dates'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(generalization_frame, text="Обобщить даты посещений по кварталам", 
                       variable=methods['generalize_dates']).pack(anchor=tk.W)
        
        # Маскирование и псевдонимизация
        masking_frame = ttk.LabelFrame(options_window, text="Маскирование и псевдонимизация", padding="10")
        masking_frame.pack(fill=tk.X, padx=20, pady=5)
        
        methods['mask_payment'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(masking_frame, text="Маскировать номера карт оплаты", 
                       variable=methods['mask_payment']).pack(anchor=tk.W)
        
        methods['pseudonymize_surname'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(masking_frame, text="Псевдонимизировать фамилии пациентов", 
                       variable=methods['pseudonymize_surname']).pack(anchor=tk.W)
        
        ttk.Separator(options_window, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Кнопки
        buttons_frame = ttk.Frame(options_window)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Применить обезличивание", 
                  command=lambda: self.apply_depersonalization(methods, options_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", 
                  command=options_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def apply_depersonalization(self, methods, window):
        """Применяет выбранные методы обезличивания к медицинским данным"""
        try:
            window.destroy()
            self.status_var.set("Выполняется обезличивание медицинских данных...")
            self.root.update()
            
            # Создаем копию исходных данных
            self.df = self.original_df.copy()
            
            # Применяем методы подавления
            cols_to_remove = []
            
            if methods['suppress_names'].get():
                for col in ['Имя', 'Отчество']:
                    if col in self.df.columns:
                        cols_to_remove.append(col)
            
            if methods['suppress_docs'].get():
                if 'СНИЛС' in self.df.columns:
                    cols_to_remove.append('СНИЛС')
            
            if methods['suppress_medical'].get():
                for col in ['Анализы', 'Врач', 'Дата готовности анализов']:
                    if col in self.df.columns:
                        cols_to_remove.append(col)
            
            if cols_to_remove:
                self.df = dp.delete_columns(self.df, cols_to_remove)
            
            # Применяем методы обобщения
            if methods['generalize_passport'].get() and 'Паспортные данные' in self.df.columns:
                self.df = dp.generalize_passport_data(self.df, 'Паспортные данные')
            
            if methods['generalize_symptoms'].get() and 'Симптомы' in self.df.columns:
                self.df = dp.generalize_symptoms(self.df, 'Симптомы', True)
            
            if methods['generalize_costs'].get() and 'Стоимость анализов' in self.df.columns:
                self.df, _, _ = dp.generalize_costs_quantile(self.df, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
            
            if methods['generalize_dates'].get() and 'Дата посещения врача' in self.df.columns:
                self.df = dp.microaggregation_of_datas(self.df, 'Дата посещения врача', True)
            
            # Применяем маскирование и псевдонимизацию
            if methods['mask_payment'].get() and 'Карта оплаты' in self.df.columns:
                self.df = dp.masking_data(self.df, ['Карта оплаты'], 1, 50)
            
            if methods['pseudonymize_surname'].get() and 'Фамилия' in self.df.columns:
                self.df = dp.pseudoname(self.df, 'Фамилия')
            
            self.status_var.set("Обезличивание медицинских данных завершено")
            
            # Автоматически пересчитываем k-anonymity
            selected_cols = self.get_selected_quasi_identifiers()
            if selected_cols:
                self.calculate_k_anonymity()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обезличивании: {str(e)}")
            self.status_var.set("Ошибка обезличивания")
    
    def save_dataset(self):
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить обезличенные медицинские данные",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("Сохранение обезличенных данных...")
                self.root.update()
                
                self.df.to_excel(file_path, index=False)
                self.output_file = file_path
                
                # Обновляем имя выходного файла
                filename = Path(file_path).name
                self.output_label.config(text=filename)
                
                self.status_var.set(f"Обезличенные медицинские данные сохранены: {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
                self.status_var.set("Ошибка сохранения файла")

def main():
    root = tk.Tk()
    app = DepersonalizationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()