# import pandas as pd
# from pathlib import Path
# from src import depersonalization as dp

# filepath = "files/dataset_100k.xlsx"


# df = pd.read_excel(filepath)
# df = dp.decompose_dates(df, 'Дата посещения врача', 'Квартал')
# df = dp.delete_columns(df, ['Дата готовности анализов'])
# df = dp.decompose_bank_card(df, 'Карта оплаты', 'Платежная система')
# df = dp.mask_passport_data(df, 'Паспортные данные', 1)
# df = dp.generalize_snils(df, 'СНИЛС')
 
# df = dp.combine_fio_to_uid(df, 'Фамилия', 'Имя', 'Отчество')
# df = dp.categorize_costs_quantile(df, 'Стоимость анализов', 3)
# df = dp.generalize_doctors_strong(df, 'Врач')
# df["Симптомы"] = df["Врач"]
# df["Анализы"] = df["Врач"]

# df, rep = dp.suppress_worst_k_groups_by_rows(df, ['Паспортные данные', 'СНИЛС', 
#          'Дата посещения врача', 'Стоимость анализов', 'Врач',
#         'Платежная система'], len(df) * 0.03)
# print(rep)

# print(dp.calculate_k_anonymity_from_df_debug(df, ['Паспортные данные', 'СНИЛС', 
#          'Дата посещения врача', 'Стоимость анализов', 'Врач',
#         'Платежная система']))

# print(dp.worst_k_anonymity_groups(df, ['Паспортные данные', 'СНИЛС', 
#          'Дата посещения врача', 'Стоимость анализов', 'Врач',
#         'Платежная система'], n=10))

# print(dp.visualize_distributions(df, ['Паспортные данные', 'СНИЛС', 
#          'Дата посещения врача', 'Стоимость анализов', 'Врач',
#         'Платежная система']))

# print(dp.visualize_k_group_sizes(df, ['Паспортные данные', 'СНИЛС', 
#          'Дата посещения врача', 'Стоимость анализов', 'Врач',
#         'Платежная система'], top_n=100))


# # dp.copy_and_save_current_state(df)





# # ...existing code...
# import os
# from pathlib import Path
# import pandas as pd
# from src import depersonalization as dp
# # ...existing code...

# DEFAULT_FILE = "files/dataset_100k.xlsx"

# # ---------------- Новые утилиты для очереди шагов ----------------

# def _print_step(idx: int, step: dict) -> None:
#     print(f"{idx}. {step.get('summary','<шаг>')}")

# def _print_queue(queue: list[dict]) -> None:
#     if not queue:
#         print("Очередь пуста.")
#         return
#     print("\nТекущая очередь шагов:")
#     for i, st in enumerate(queue, 1):
#         _print_step(i, st)

# def _apply_single_call(df: pd.DataFrame, fn, *args, **kwargs) -> tuple[pd.DataFrame, dict | None, object | None]:
#     """Вызывает функцию, возвращает (df, report, raw_result)."""
#     res = fn(df, *args, **kwargs)
#     # Поддержка функций, возвращающих (df, report) или просто df/путь/число
#     if isinstance(res, tuple) and len(res) >= 1 and isinstance(res[0], pd.DataFrame):
#         df2 = res[0]
#         report = res[1] if len(res) > 1 else None
#         return df2, report, res
#     if isinstance(res, pd.DataFrame):
#         return res, None, res
#     # Аналитические функции не меняют df
#     return df, None, res

# def _apply_step(df: pd.DataFrame, step: dict) -> pd.DataFrame:
#     """Применяет один шаг к df (или выполняет анализ/визуализацию)."""
#     stype = step.get("type", "transform")
#     fn_name = step["fn"]
#     fn = getattr(dp, fn_name)
#     mode = step.get("mode", "direct")
#     params = dict(step.get("params", {}))  # копия
#     # Специальная обработка доли строк для подавления
#     if fn_name == "suppress_worst_k_groups_by_rows" and "rows_frac" in params and "rows_to_remove" not in params:
#         frac = float(params.pop("rows_frac"))
#         params["rows_to_remove"] = max(1, int(len(df) * frac))

#     if stype == "transform":
#         if mode == "per_column":
#             columns = params.pop("columns", [])
#             for col in columns:
#                 df, report, _ = _apply_single_call(df, fn, col if step.get("pos_second", True) else None, **params) if False else _apply_single_call(df, fn, col, **params)
#             return df
#         elif mode == "list_arg":
#             columns = params.pop("columns", [])
#             df, report, _ = _apply_single_call(df, fn, columns, **params)
#             return df
#         else:
#             df, report, _ = _apply_single_call(df, fn, **params)
#             # Если функция возвращала report — кратко покажем
#             if report is not None:
#                 print("Report:", {k: v for k, v in report.items() if k != "removed_k_hist"})
#                 if "removed_k_hist" in report:
#                     print("removed_k_hist:")
#                     print(report["removed_k_hist"])
#             return df
#     else:
#         # Аналитические/визуальные шаги
#         _, _, raw = _apply_single_call(df, fn, **params)
#         if fn_name == "calculate_k_anonymity_from_df_debug":
#             # Дополнительно показать худшие группы, если задано
#             n = step.get("extra", {}).get("worst_n")
#             qi = params.get("quasi_identifiers") or params.get("quasi_identifiers".replace("_", ""))
#             if n and qi:
#                 print(dp.worst_k_anonymity_groups(df, qi, n=int(n)))
#         elif fn_name == "visualize_distributions":
#             print("Файлы сохранены:", raw)
#         elif fn_name == "visualize_k_group_sizes":
#             print("Файл сохранен:", raw)
#         return df

# def _build_step(df: pd.DataFrame, choice: str) -> dict | None:
#     """Запрашивает аргументы и возвращает шаг очереди (dict)."""
#     # 1) Обобщить даты
#     if choice == "1":
#         cols = input_columns(df, "Выберите колонку даты (номер/имя): ")
#         if not cols:
#             return None
#         level = ask_choice("Уровень обобщения даты", ["Год", "Квартал", "Месяц", "День"], default_index=1)
#         return {
#             "type": "transform",
#             "fn": "decompose_dates",
#             "mode": "per_column",
#             "params": {"columns": cols, "element": level},
#             "summary": f"Обобщить даты {cols} → {level}",
#         }
#     # 2) Удалить колонки
#     if choice == "2":
#         cols = input_columns(df, "Колонки для удаления (номера/имена через запятую): ")
#         if not cols:
#             return None
#         return {
#             "type": "transform",
#             "fn": "delete_columns",
#             "mode": "list_arg",
#             "params": {"columns": cols},
#             "summary": f"Удалить колонки {cols}",
#         }
#     # 3) Разложить карту
#     if choice == "3":
#         cols = input_columns(df, "Колонка с картой (обычно 'Карта оплаты'): ")
#         if not cols:
#             return None
#         element = ask_choice("Что извлечь?", ["Платежная система", "Банк"], default_index=0)
#         return {
#             "type": "transform",
#             "fn": "decompose_bank_card",
#             "mode": "per_column",
#             "params": {"columns": cols, "element": element},
#             "summary": f"Разложить карту {cols} → {element}",
#         }
#     # 4) Маскировать паспорт
#     if choice == "4":
#         cols = input_columns(df, "Колонка паспорта (обычно 'Паспортные данные'): ")
#         if not cols:
#             return None
#         n = ask_int("Сколько первых символов оставить?", default=1, min_val=0)
#         return {
#             "type": "transform",
#             "fn": "mask_passport_data",
#             "mode": "per_column",
#             "params": {"columns": cols, "length": n},
#             "summary": f"Маскирование паспорта {cols}, оставить {n}",
#         }
#     # 5) Обобщить СНИЛС
#     if choice == "5":
#         cols = input_columns(df, "Колонка СНИЛС (обычно 'СНИЛС'): ")
#         if not cols:
#             return None
#         return {
#             "type": "transform",
#             "fn": "generalize_snils",
#             "mode": "per_column",
#             "params": {"columns": cols},
#             "summary": f"Обобщение СНИЛС {cols}",
#         }
#     # 6) UID из ФИО
#     if choice == "6":
#         list_columns(df)
#         s = input("Имя колонки Фамилия [Фамилия]: ").strip() or "Фамилия"
#         n = input("Имя колонки Имя [Имя]: ").strip() or "Имя"
#         p = input("Имя колонки Отчество [Отчество]: ").strip() or "Отчество"
#         new_col = input("Имя нового столбца [UID]: ").strip() or "UID"
#         return {
#             "type": "transform",
#             "fn": "combine_fio_to_uid",
#             "mode": "direct",
#             "params": {"surname_col": s, "name_col": n, "patronymic_col": p, "new_col": new_col},
#             "summary": f"UID из ФИО → {new_col}",
#         }
#     # 7) Стоимость по квантилям
#     if choice == "7":
#         cols = input_columns(df, "Колонка стоимости (обычно 'Стоимость анализов'): ")
#         if not cols:
#             return None
#         bins = ask_int("Количество квантильных корзин", default=3, min_val=2, max_val=10)
#         return {
#             "type": "transform",
#             "fn": "categorize_costs_quantile",
#             "mode": "per_column",
#             "params": {"columns": cols, "num_bins": bins},
#             "summary": f"Квантильная категоризация {cols}, корзин={bins}",
#         }
#     # 8) Обобщить врача
#     if choice == "8":
#         cols = input_columns(df, "Колонка со специальностью врача (обычно 'Врач'): ")
#         if not cols:
#             return None
#         return {
#             "type": "transform",
#             "fn": "generalize_doctors_strong",
#             "mode": "per_column",
#             "params": {"columns": cols},
#             "summary": f"Обобщение врача {cols}",
#         }
#     # 9) Подавление по строкам
#     if choice == "9":
#         qi = input_columns(df, "Квази-идентификаторы для подавления (через запятую): ")
#         if not qi:
#             return None
#         mode = ask_choice("Как задать объем подавления?", ["Долей от датасета", "Точным числом строк"], 0)
#         params = {"quasi_identifiers": qi, "allow_overshoot": True}
#         if mode == "Долей от датасета":
#             frac = ask_float("Доля строк (0-1)", default=0.03, min_val=0.0, max_val=1.0)
#             params["rows_frac"] = frac
#             summ = f"Подавить худшие k-группы ~{int(frac*100)}% строк"
#         else:
#             rows = ask_int("Число строк для удаления", min_val=1, max_val=max(1, len(df)))
#             params["rows_to_remove"] = rows
#             summ = f"Подавить худшие k-группы {rows} строк"
#         params["allow_overshoot"] = ask_yes_no("Разрешить превышение на размер последней группы?", True)
#         return {
#             "type": "transform",
#             "fn": "suppress_worst_k_groups_by_rows",
#             "mode": "direct",
#             "params": params,
#             "summary": f"{summ}; QI={qi}",
#         }
#     # 10) k-анонимность + худшие группы
#     if choice == "10":
#         qi = input_columns(df, "Квази-идентификаторы для расчета k (через запятую): ")
#         if not qi:
#             return None
#         n = ask_int("Сколько худших групп показать?", default=10, min_val=1, max_val=100)
#         return {
#             "type": "analysis",
#             "fn": "calculate_k_anonymity_from_df_debug",
#             "mode": "direct",
#             "params": {"quasi_identifiers": qi},
#             "extra": {"worst_n": n},
#             "summary": f"k-анонимность и топ-{n} худших групп; QI={qi}",
#         }
#     # 11) Визуализация распределений
#     if choice == "11":
#         cols = input_columns(df, "Колонки для визуализации (Enter=все): ", allow_empty=True)
#         out_dir = input("Каталог для графиков [files/plots]: ").strip() or "files/plots"
#         return {
#             "type": "analysis",
#             "fn": "visualize_distributions",
#             "mode": "direct",
#             "params": {"columns": (cols or None), "output_dir": out_dir},
#             "summary": f"Гистограммы распределений {cols or 'ВСЕ'} → {out_dir}",
#         }
#     # 12) Визуализация k-распределения
#     if choice == "12":
#         qi = input_columns(df, "Квази-идентификаторы для графика k (через запятую): ")
#         if not qi:
#             return None
#         top_n = ask_int("Сколько разных k показывать?", default=25, min_val=5, max_val=200)
#         out = input("Путь к файлу графика [files/plots/k_distribution.png]: ").strip() or "files/plots/k_distribution.png"
#         return {
#             "type": "analysis",
#             "fn": "visualize_k_group_sizes",
#             "mode": "direct",
#             "params": {"quasi_identifiers": qi, "output_path": out, "top_n": top_n},
#             "summary": f"k-распределение (top_n={top_n}); QI={qi} → {out}",
#         }
#     return None

# # ---------------- Конец утилит для очереди шагов ----------------

# def load_dataset(path: str) -> pd.DataFrame:
#     print(f"Загрузка: {path}")
#     df_local = pd.read_excel(path)
#     print(f"Загружено строк: {len(df_local)}, колонок: {len(df_local.columns)}")
#     return df_local

# def list_columns(df: pd.DataFrame) -> None:
#     print("\nКолонки:")
#     for i, c in enumerate(df.columns, 1):
#         print(f"  {i}. {c}")
#     print("")

# def input_columns(df: pd.DataFrame, prompt: str, allow_empty: bool = False) -> list[str]:
#     """
#     Ввод списка колонок: номера через запятую или имена.
#     """
#     list_columns(df)
#     while True:
#         raw = input(prompt).strip()
#         if allow_empty and raw == "":
#             return []
#         parts = [p.strip() for p in raw.split(",") if p.strip()]
#         selected: list[str] = []
#         ok = True
#         for p in parts:
#             if p.isdigit():
#                 idx = int(p) - 1
#                 if 0 <= idx < len(df.columns):
#                     selected.append(df.columns[idx])
#                 else:
#                     ok = False
#                     break
#             else:
#                 if p in df.columns:
#                     selected.append(p)
#                 else:
#                     ok = False
#                     break
#         if ok and (allow_empty or selected):
#             return selected
#         print("Некорректный ввод. Укажите номера/имена колонок через запятую.")

# def ask_int(prompt: str, default: int | None = None, min_val: int | None = None, max_val: int | None = None) -> int:
#     while True:
#         raw = input(f"{prompt}{' ['+str(default)+']' if default is not None else ''}: ").strip()
#         if raw == "" and default is not None:
#             return default
#         try:
#             val = int(float(raw))
#             if min_val is not None and val < min_val:
#                 print(f"Минимум: {min_val}")
#                 continue
#             if max_val is not None and val > max_val:
#                 print(f"Максимум: {max_val}")
#                 continue
#             return val
#         except ValueError:
#             print("Введите целое число.")

# def ask_float(prompt: str, default: float | None = None, min_val: float | None = None, max_val: float | None = None) -> float:
#     while True:
#         raw = input(f"{prompt}{' ['+str(default)+']' if default is not None else ''}: ").strip()
#         if raw == "" and default is not None:
#             return default
#         try:
#             val = float(raw)
#             if min_val is not None and val < min_val:
#                 print(f"Минимум: {min_val}")
#                 continue
#             if max_val is not None and val > max_val:
#                 print(f"Максимум: {max_val}")
#                 continue
#             return val
#         except ValueError:
#             print("Введите число.")

# def ask_choice(prompt: str, options: list[str], default_index: int = 0) -> str:
#     for i, opt in enumerate(options, 1):
#         mark = "*" if (i - 1) == default_index else " "
#         print(f"  {i}. {opt} {mark}")
#     while True:
#         raw = input(f"{prompt} [по номеру, Enter={default_index+1}]: ").strip()
#         if raw == "":
#             return options[default_index]
#         if raw.isdigit():
#             idx = int(raw) - 1
#             if 0 <= idx < len(options):
#                 return options[idx]
#         print("Некорректный выбор.")

# def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
#     while True:
#         raw = input(f"{prompt} [{'Y/n' if default_yes else 'y/N'}]: ").strip().lower()
#         if raw == "" and default_yes:
#             return True
#         if raw == "" and not default_yes:
#             return False
#         if raw in ("y", "yes", "д", "да"):
#             return True
#         if raw in ("n", "no", "н", "нет"):
#             return False
#         print("Введите y/n.")

# def menu() -> None:
#     print("\n=== Консольный интерфейс обезличивания ===")
#     data_path = input(f"Путь к файлу Excel [{DEFAULT_FILE}]: ").strip() or DEFAULT_FILE
#     df = load_dataset(data_path)
#     original_df = df.copy()
#     queue: list[dict] = []

#     while True:
#         print("\nВыберите действие:")
#         print(" 1) Обобщить даты (Год/Квартал/Месяц/День)")
#         print(" 2) Удалить колонки")
#         print(" 3) Разложить поле карты (Платежная система/Банк)")
#         print(" 4) Маскировать паспортные данные")
#         print(" 5) Обобщить СНИЛС")
#         print(" 6) Сформировать UID из ФИО")
#         print(" 7) Категоризовать стоимость по квантилям")
#         print(" 8) Жестко обобщить специальность врача")
#         print(" 9) Подавить записи худших k-групп (по числу строк)")
#         print("10) Посчитать k-anonymity и показать худшие группы")
#         print("11) Визуализация распределений по столбцам")
#         print("12) Визуализация распределения размеров k-групп")
#         print("13) Показать первые строки и список колонок")
#         print("14) Сохранить датасет")
#         print("15) Сбросить изменения (перезагрузить исходный файл)")
#         print("16) Режим очереди (добавить несколько шагов и применить)")
#         print(" 0) Выход")

#         choice = input("Ваш выбор: ").strip()

#         try:
#             if choice in {str(i) for i in range(1, 13)}:
#                 # Немедленное применение (как раньше)
#                 step = _build_step(df, choice)
#                 if step:
#                     if step["type"] == "transform":
#                         df = _apply_step(df, step)
#                     else:
#                         _apply_step(df, step)
#                 continue

#             if choice == "13":
#                 print(df.head())
#                 list_columns(df)
#                 continue

#             if choice == "14":
#                 out = input("Путь для сохранения Excel [files/dataset_processed.xlsx]: ").strip() or "files/dataset_processed.xlsx"
#                 Path(Path(out).parent).mkdir(parents=True, exist_ok=True)
#                 dp.save_current_state(df, out)
#                 print(f"Сохранено: {out}")
#                 continue

#             if choice == "15":
#                 df = load_dataset(data_path)
#                 original_df = df.copy()
#                 print("Данные перезагружены из исходного файла.")
#                 continue

#             if choice == "16":
#                 # Подменю очереди
#                 while True:
#                     print("\n— Режим очереди —")
#                     print(" a) Добавить шаг (по номерам 1..12)")
#                     print(" s) Показать очередь")
#                     print(" d) Удалить шаг по номеру")
#                     print(" r) Выполнить очередь")
#                     print(" c) Очистить очередь")
#                     print(" q) Выход в главное меню")
#                     sub = input("Выбор: ").strip().lower()

#                     if sub == "a":
#                         add_choice = input("Номер шага для добавления (1..12): ").strip()
#                         if add_choice in {str(i) for i in range(1, 13)}:
#                             st = _build_step(df, add_choice)
#                             if st:
#                                 queue.append(st)
#                                 print("Добавлено:")
#                                 _print_step(len(queue), st)
#                         else:
#                             print("Некорректный номер шага.")
#                     elif sub == "s":
#                         _print_queue(queue)
#                     elif sub == "d":
#                         _print_queue(queue)
#                         ridx = ask_int("Номер шага для удаления", min_val=1, max_val=max(1, len(queue))) if queue else None
#                         if queue and 1 <= ridx <= len(queue):
#                             removed = queue.pop(ridx-1)
#                             print("Удалено:")
#                             _print_step(ridx, removed)
#                     elif sub == "r":
#                         if not queue:
#                             print("Очередь пуста.")
#                             continue
#                         print("Выполнение очереди...")
#                         for i, st in enumerate(queue, 1):
#                             print(f"[{i}/{len(queue)}] {st['summary']}")
#                             df = _apply_step(df, st)
#                         print("Готово.")
#                     elif sub == "c":
#                         queue.clear()
#                         print("Очередь очищена.")
#                     elif sub == "q":
#                         break
#                     else:
#                         print("Неизвестная команда.")
#                 continue

#             if choice == "0":
#                 print("Выход.")
#                 break

#             print("Неизвестная команда.")

#         except Exception as e:
#             print(f"Ошибка: {e}")

# if __name__ == "__main__":
#     menu()
# # ...existing code...


# def load_dataset(path: str) -> pd.DataFrame:
#     print(f"Загрузка: {path}")
#     df_local = pd.read_excel(path)
#     print(f"Загружено строк: {len(df_local)}, колонок: {len(df_local.columns)}")
#     return df_local


# def list_columns(df: pd.DataFrame) -> None:
#     print("\nКолонки:")
#     for i, c in enumerate(df.columns, 1):
#         print(f"  {i}. {c}")
#     print("")


# def input_columns(df: pd.DataFrame, prompt: str, allow_empty: bool = False) -> list[str]:
#     """
#     Ввод списка колонок: номера через запятую или имена.
#     """
#     list_columns(df)
#     while True:
#         raw = input(prompt).strip()
#         if allow_empty and raw == "":
#             return []
#         # номера
#         parts = [p.strip() for p in raw.split(",") if p.strip()]
#         selected: list[str] = []
#         ok = True
#         for p in parts:
#             if p.isdigit():
#                 idx = int(p) - 1
#                 if 0 <= idx < len(df.columns):
#                     selected.append(df.columns[idx])
#                 else:
#                     ok = False
#                     break
#             else:
#                 if p in df.columns:
#                     selected.append(p)
#                 else:
#                     ok = False
#                     break
#         if ok and (allow_empty or selected):
#             return selected
#         print("Некорректный ввод. Укажите номера/имена колонок через запятую.")


# def ask_int(prompt: str, default: int | None = None, min_val: int | None = None, max_val: int | None = None) -> int:
#     while True:
#         raw = input(f"{prompt}{' ['+str(default)+']' if default is not None else ''}: ").strip()
#         if raw == "" and default is not None:
#             return default
#         try:
#             val = int(float(raw))
#             if min_val is not None and val < min_val:
#                 print(f"Минимум: {min_val}")
#                 continue
#             if max_val is not None and val > max_val:
#                 print(f"Максимум: {max_val}")
#                 continue
#             return val
#         except ValueError:
#             print("Введите целое число.")


# def ask_float(prompt: str, default: float | None = None, min_val: float | None = None, max_val: float | None = None) -> float:
#     while True:
#         raw = input(f"{prompt}{' ['+str(default)+']' if default is not None else ''}: ").strip()
#         if raw == "" and default is not None:
#             return default
#         try:
#             val = float(raw)
#             if min_val is not None and val < min_val:
#                 print(f"Минимум: {min_val}")
#                 continue
#             if max_val is not None and val > max_val:
#                 print(f"Максимум: {max_val}")
#                 continue
#             return val
#         except ValueError:
#             print("Введите число.")


# def ask_choice(prompt: str, options: list[str], default_index: int = 0) -> str:
#     for i, opt in enumerate(options, 1):
#         mark = "*" if (i - 1) == default_index else " "
#         print(f"  {i}. {opt} {mark}")
#     while True:
#         raw = input(f"{prompt} [по номеру, Enter={default_index+1}]: ").strip()
#         if raw == "":
#             return options[default_index]
#         if raw.isdigit():
#             idx = int(raw) - 1
#             if 0 <= idx < len(options):
#                 return options[idx]
#         print("Некорректный выбор.")


# def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
#     while True:
#         raw = input(f"{prompt} [{'Y/n' if default_yes else 'y/N'}]: ").strip().lower()
#         if raw == "" and default_yes:
#             return True
#         if raw == "" and not default_yes:
#             return False
#         if raw in ("y", "yes", "д", "да"):
#             return True
#         if raw in ("n", "no", "н", "нет"):
#             return False
#         print("Введите y/n.")


# def menu() -> None:
#     print("\n=== Консольный интерфейс обезличивания ===")
#     data_path = input(f"Путь к файлу Excel [{DEFAULT_FILE}]: ").strip() or DEFAULT_FILE
#     df = load_dataset(data_path)
#     original_df = df.copy()

#     while True:
#         print("\nВыберите действие:")
#         print(" 1) Обобщить даты (Год/Квартал/Месяц/День)")
#         print(" 2) Удалить колонки")
#         print(" 3) Разложить поле карты (Платежная система/Банк)")
#         print(" 4) Маскировать паспортные данные")
#         print(" 5) Обобщить СНИЛС")
#         print(" 6) Сформировать UID из ФИО")
#         print(" 7) Категоризовать стоимость по квантилям")
#         print(" 8) Жестко обобщить специальность врача")
#         print(" 9) Подавить записи худших k-групп (по числу строк)")
#         print("10) Посчитать k-anonymity и показать худшие группы")
#         print("11) Визуализация распределений по столбцам")
#         print("12) Визуализация распределения размеров k-групп")
#         print("13) Показать первые строки и список колонок")
#         print("14) Сохранить датасет")
#         print("15) Сбросить изменения (перезагрузить исходный файл)")
#         print(" 0) Выход")

#         choice = input("Ваш выбор: ").strip()

#         try:
#             if choice == "1":
#                 cols = input_columns(df, "Выберите колонку даты (номер/имя): ")
#                 if not cols:
#                     continue
#                 level = ask_choice("Уровень обобщения даты",
#                                    ["Год", "Квартал", "Месяц", "День"], default_index=1)
#                 for c in cols:
#                     df = dp.decompose_dates(df, c, level)
#                 print("Готово.")

#             elif choice == "2":
#                 cols = input_columns(df, "Колонки для удаления (номера/имена через запятую): ")
#                 if cols:
#                     df = dp.delete_columns(df, cols)
#                     print("Удалено.")

#             elif choice == "3":
#                 cols = input_columns(df, "Колонка с картой (обычно 'Карта оплаты'): ")
#                 if not cols:
#                     continue
#                 element = ask_choice("Что извлечь?", ["Платежная система", "Банк"], default_index=0)
#                 for c in cols:
#                     df = dp.decompose_bank_card(df, c, element)
#                 print("Готово.")

#             elif choice == "4":
#                 cols = input_columns(df, "Колонка паспорта (обычно 'Паспортные данные'): ")
#                 if not cols:
#                     continue
#                 n = ask_int("Сколько первых символов оставить (остальное замаскировать)?", default=1, min_val=0)
#                 for c in cols:
#                     df = dp.mask_passport_data(df, c, n)
#                 print("Готово.")

#             elif choice == "5":
#                 cols = input_columns(df, "Колонка СНИЛС (обычно 'СНИЛС'): ")
#                 for c in cols:
#                     df = dp.generalize_snils(df, c)
#                 print("Готово.")

#             elif choice == "6":
#                 list_columns(df)
#                 s = input("Имя колонки Фамилия [Фамилия]: ").strip() or "Фамилия"
#                 n = input("Имя колонки Имя [Имя]: ").strip() or "Имя"
#                 p = input("Имя колонки Отчество [Отчество]: ").strip() or "Отчество"
#                 new_col = input("Имя нового столбца [UID]: ").strip() or "UID"
#                 df = dp.combine_fio_to_uid(df, s, n, p, new_col)
#                 print("Готово.")

#             elif choice == "7":
#                 cols = input_columns(df, "Колонка стоимости (обычно 'Стоимость анализов'): ")
#                 if not cols:
#                     continue
#                 bins = ask_int("Количество квантильных корзин", default=3, min_val=2, max_val=10)
#                 for c in cols:
#                     df = dp.categorize_costs_quantile(df, c, bins)
#                 print("Готово.")

#             elif choice == "8":
#                 cols = input_columns(df, "Колонка со специальностью врача (обычно 'Врач'): ")
#                 for c in cols:
#                     df = dp.generalize_doctors_strong(df, c)
#                 print("Готово.")

#             elif choice == "9":
#                 qi = input_columns(df, "Выберите квази-идентификаторы для группировки (через запятую): ")
#                 if not qi:
#                     continue
#                 mode = ask_choice("Как задать объем подавления?", ["Долей от датасета", "Точным числом строк"], 0)
#                 if mode == "Долей от датасета":
#                     frac = ask_float("Доля строк для удаления (0-1)", default=0.03, min_val=0.0, max_val=1.0)
#                     rows_target = int(len(df) * frac)
#                 else:
#                     rows_target = ask_int("Число строк для удаления", min_val=1, max_val=len(df))
#                 overshoot = ask_yes_no("Разрешить превысить целевое число на размер последней группы?", True)
#                 df, rep = dp.suppress_worst_k_groups_by_rows(df, qi, rows_to_remove=rows_target, allow_overshoot=overshoot)
#                 print("Отчет подавления:")
#                 for k, v in rep.items():
#                     if k == "removed_k_hist":
#                         print(f"  {k}:")
#                         print(rep["removed_k_hist"])
#                     else:
#                         print(f"  {k}: {v}")

#             elif choice == "10":
#                 qi = input_columns(df, "Квази-идентификаторы для расчета k (через запятую): ")
#                 if not qi:
#                     continue
#                 k = dp.calculate_k_anonymity_from_df_debug(df, qi)
#                 n = ask_int("Сколько худших групп показать?", default=10, min_val=1, max_val=100)
#                 print(dp.worst_k_anonymity_groups(df, qi, n=n))

#             elif choice == "11":
#                 cols = input_columns(df, "Колонки для визуализации распределений (Enter=все): ", allow_empty=True)
#                 out_dir = input("Каталог для графиков [files/plots]: ").strip() or "files/plots"
#                 paths = dp.visualize_distributions(df, cols or None, output_dir=out_dir)
#                 print("Сохраненные файлы:")
#                 for p in paths:
#                     print(" ", p)

#             elif choice == "12":
#                 qi = input_columns(df, "Квази-идентификаторы для графика k (через запятую): ")
#                 if not qi:
#                     continue
#                 top_n = ask_int("Сколько разных k показывать (хвост агрегируется)?", default=25, min_val=5, max_val=200)
#                 out = input("Путь к файлу графика [files/plots/k_distribution.png]: ").strip() or "files/plots/k_distribution.png"
#                 path = dp.visualize_k_group_sizes(df, qi, output_path=out, top_n=top_n)
#                 print(f"Сохранено: {path}")

#             elif choice == "13":
#                 print(df.head())
#                 list_columns(df)

#             elif choice == "14":
#                 out = input("Путь для сохранения Excel [files/dataset_processed.xlsx]: ").strip() or "files/dataset_processed.xlsx"
#                 Path(Path(out).parent).mkdir(parents=True, exist_ok=True)
#                 dp.save_current_state(df, out)
#                 print(f"Сохранено: {out}")

#             elif choice == "15":
#                 df = load_dataset(data_path)
#                 original_df = df.copy()
#                 print("Данные перезагружены из исходного файла.")

#             elif choice == "0":
#                 print("Выход.")
#                 break

#             else:
#                 print("Неизвестная команда.")

#         except Exception as e:
#             print(f"Ошибка: {e}")


# if __name__ == "__main__":
#     menu()






import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
from src import depersonalization as dp


class AnonymizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Обезличивание медицинских данных (Tkinter)")
        self.root.geometry("1180x720")

        self.df: pd.DataFrame | None = None
        self.original_df: pd.DataFrame | None = None
        self.filepath: str | None = None

        # UI vars
        self.status_var = tk.StringVar(value="Загрузите Excel файл...")
        # Transform controls vars
        self.var_date_col = tk.StringVar()
        self.var_date_level = tk.StringVar(value="Квартал")

        self.var_del_cols = None  # Listbox

        self.var_card_col = tk.StringVar()
        self.var_card_element = tk.StringVar(value="Платежная система")

        self.var_pass_col = tk.StringVar()
        self.var_pass_len = tk.IntVar(value=1)

        self.var_snils_col = tk.StringVar()

        self.var_fam_col = tk.StringVar(value="Фамилия")
        self.var_name_col = tk.StringVar(value="Имя")
        self.var_otch_col = tk.StringVar(value="Отчество")
        self.var_uid_col = tk.StringVar(value="UID")

        self.var_cost_col = tk.StringVar()
        self.var_cost_bins = tk.IntVar(value=3)

        self.var_doc_col = tk.StringVar()

        # Suppression
        self.var_qi_supp = None  # Listbox
        self.var_supp_mode = tk.StringVar(value="frac")
        self.var_supp_frac = tk.DoubleVar(value=0.03)
        self.var_supp_rows = tk.IntVar(value=100)
        self.var_supp_overshoot = tk.BooleanVar(value=True)

        # Analytics
        self.var_qi_calc = None  # Listbox
        self.var_top_n_k = tk.IntVar(value=10)

        # Visual distributions
        self.var_vis_cols = None  # Listbox
        self.var_plots_dir = tk.StringVar(value="files/plots")

        # Visual k sizes
        self.var_top_n_vis = tk.IntVar(value=25)
        self.var_k_plot_path = tk.StringVar(value="files/plots/k_distribution.png")

        self._build_ui()

    # ------------------------- UI -------------------------

    def _build_ui(self):
        # Top bar (file)
        top = ttk.Frame(self.root, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(top, text="Открыть Excel", command=self.on_open).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top, text="Сохранить Excel", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Сбросить (перезагрузить)", command=self.on_reset).pack(side=tk.LEFT, padx=5)

        self.lbl_file = ttk.Label(top, text="Файл: —")
        self.lbl_file.pack(side=tk.LEFT, padx=10)

        ttk.Label(top, textvariable=self.status_var, foreground="#555").pack(side=tk.RIGHT)

        # Main panes
        main = ttk.Frame(self.root)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left: Transformations
        left = ttk.LabelFrame(main, text="Преобразования", padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=8)

        # Transform: Dates
        lf_dates = ttk.LabelFrame(left, text="Обобщение даты", padding=6)
        lf_dates.pack(fill=tk.X, pady=4)
        ttk.Label(lf_dates, text="Колонка даты").grid(row=0, column=0, sticky="w")
        self.cb_date_col = ttk.Combobox(lf_dates, textvariable=self.var_date_col, state="readonly")
        self.cb_date_col.grid(row=0, column=1, sticky="ew", padx=4)
        lf_dates.columnconfigure(1, weight=1)
        ttk.Label(lf_dates, text="Уровень").grid(row=1, column=0, sticky="w")
        self.cb_date_level = ttk.Combobox(lf_dates, textvariable=self.var_date_level, state="readonly",
                                          values=["Год", "Квартал", "Месяц", "День"])
        self.cb_date_level.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Button(lf_dates, text="Применить", command=self.apply_dates).grid(row=2, column=0, columnspan=2, pady=4)

        # Transform: Delete columns
        lf_del = ttk.LabelFrame(left, text="Удалить колонки", padding=6)
        lf_del.pack(fill=tk.BOTH, pady=4)
        self.var_del_cols = tk.Listbox(lf_del, selectmode=tk.EXTENDED, height=6)
        self.var_del_cols.pack(fill=tk.BOTH, expand=True)
        ttk.Button(lf_del, text="Удалить выбранные", command=self.apply_delete_columns).pack(pady=4)

        # Transform: Bank card
        lf_card = ttk.LabelFrame(left, text="Карта оплаты", padding=6)
        lf_card.pack(fill=tk.X, pady=4)
        ttk.Label(lf_card, text="Колонка").grid(row=0, column=0, sticky="w")
        self.cb_card_col = ttk.Combobox(lf_card, textvariable=self.var_card_col, state="readonly")
        self.cb_card_col.grid(row=0, column=1, sticky="ew", padx=4)
        lf_card.columnconfigure(1, weight=1)
        ttk.Label(lf_card, text="Элемент").grid(row=1, column=0, sticky="w")
        self.cb_card_element = ttk.Combobox(lf_card, textvariable=self.var_card_element, state="readonly",
                                            values=["Платежная система", "Банк"])
        self.cb_card_element.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Button(lf_card, text="Разложить", command=self.apply_decompose_card).grid(row=2, column=0, columnspan=2, pady=4)

        # Transform: Passport mask
        lf_pass = ttk.LabelFrame(left, text="Маскирование паспорта", padding=6)
        lf_pass.pack(fill=tk.X, pady=4)
        ttk.Label(lf_pass, text="Колонка").grid(row=0, column=0, sticky="w")
        self.cb_pass_col = ttk.Combobox(lf_pass, textvariable=self.var_pass_col, state="readonly")
        self.cb_pass_col.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(lf_pass, text="Оставить символов").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(lf_pass, from_=0, to=20, textvariable=self.var_pass_len, width=7).grid(row=1, column=1, sticky="w")
        ttk.Button(lf_pass, text="Маскировать", command=self.apply_mask_passport).grid(row=2, column=0, columnspan=2, pady=4)

        # Transform: SNILS
        lf_snils = ttk.LabelFrame(left, text="Обобщить СНИЛС", padding=6)
        lf_snils.pack(fill=tk.X, pady=4)
        ttk.Label(lf_snils, text="Колонка").grid(row=0, column=0, sticky="w")
        self.cb_snils_col = ttk.Combobox(lf_snils, textvariable=self.var_snils_col, state="readonly")
        self.cb_snils_col.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(lf_snils, text="Обобщить", command=self.apply_generalize_snils).grid(row=1, column=0, columnspan=2, pady=4)

        # Transform: FIO->UID
        lf_uid = ttk.LabelFrame(left, text="UID из ФИО", padding=6)
        lf_uid.pack(fill=tk.X, pady=4)
        ttk.Label(lf_uid, text="Фамилия").grid(row=0, column=0, sticky="w")
        self.cb_fam = ttk.Combobox(lf_uid, textvariable=self.var_fam_col)
        self.cb_fam.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(lf_uid, text="Имя").grid(row=1, column=0, sticky="w")
        self.cb_name = ttk.Combobox(lf_uid, textvariable=self.var_name_col)
        self.cb_name.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Label(lf_uid, text="Отчество").grid(row=2, column=0, sticky="w")
        self.cb_otch = ttk.Combobox(lf_uid, textvariable=self.var_otch_col)
        self.cb_otch.grid(row=2, column=1, sticky="ew", padx=4)
        ttk.Label(lf_uid, text="Новый столбец").grid(row=3, column=0, sticky="w")
        ttk.Entry(lf_uid, textvariable=self.var_uid_col).grid(row=3, column=1, sticky="ew", padx=4)
        lf_uid.columnconfigure(1, weight=1)
        ttk.Button(lf_uid, text="Сформировать UID", command=self.apply_fio_to_uid).grid(row=4, column=0, columnspan=2, pady=4)

        # Transform: Costs quantiles
        lf_cost = ttk.LabelFrame(left, text="Стоимость по квантилям", padding=6)
        lf_cost.pack(fill=tk.X, pady=4)
        ttk.Label(lf_cost, text="Колонка").grid(row=0, column=0, sticky="w")
        self.cb_cost_col = ttk.Combobox(lf_cost, textvariable=self.var_cost_col, state="readonly")
        self.cb_cost_col.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(lf_cost, text="Корзин").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(lf_cost, from_=2, to=10, textvariable=self.var_cost_bins, width=7).grid(row=1, column=1, sticky="w")
        ttk.Button(lf_cost, text="Категоризовать", command=self.apply_cost_quantiles).grid(row=2, column=0, columnspan=2, pady=4)

        # Transform: Doctors generalization
        lf_doc = ttk.LabelFrame(left, text="Обобщение врача", padding=6)
        lf_doc.pack(fill=tk.X, pady=4)
        ttk.Label(lf_doc, text="Колонка").grid(row=0, column=0, sticky="w")
        self.cb_doc_col = ttk.Combobox(lf_doc, textvariable=self.var_doc_col, state="readonly")
        self.cb_doc_col.grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(lf_doc, text="Обобщить", command=self.apply_generalize_doctors).grid(row=1, column=0, columnspan=2, pady=4)

        # Center: Analytics & Suppression
        center = ttk.LabelFrame(main, text="Аналитика и подавление", padding=8)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=8)

        # QI selection
        qi_frame = ttk.LabelFrame(center, text="Квази-идентификаторы (для k и подавления)", padding=6)
        qi_frame.pack(fill=tk.BOTH)
        self.lb_qi = tk.Listbox(qi_frame, selectmode=tk.EXTENDED, height=8)
        self.lb_qi.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # k-anonymity controls
        ka_frame = ttk.LabelFrame(center, text="k-anonymity", padding=6)
        ka_frame.pack(fill=tk.X, pady=6)
        ttk.Label(ka_frame, text="Показать худшие группы (N)").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(ka_frame, from_=1, to=100, textvariable=self.var_top_n_k, width=7).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Button(ka_frame, text="Рассчитать k", command=self.on_calc_k).grid(row=0, column=2, padx=6)
        self.txt_k = tk.Text(ka_frame, height=10)
        self.txt_k.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=4)
        ka_frame.columnconfigure(2, weight=1)

        # Suppression controls
        sup_frame = ttk.LabelFrame(center, text="Подавление худших k-групп", padding=6)
        sup_frame.pack(fill=tk.X, pady=6)
        ttk.Radiobutton(sup_frame, text="Доля строк", variable=self.var_supp_mode, value="frac").grid(row=0, column=0, sticky="w")
        ttk.Entry(sup_frame, textvariable=self.var_supp_frac, width=8).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(sup_frame, text="Точное число строк", variable=self.var_supp_mode, value="rows").grid(row=1, column=0, sticky="w")
        ttk.Entry(sup_frame, textvariable=self.var_supp_rows, width=8).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(sup_frame, text="Разрешить превышение на размер последней группы", variable=self.var_supp_overshoot).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Button(sup_frame, text="Выполнить подавление", command=self.on_suppress).grid(row=3, column=0, columnspan=2, pady=6)

        # Right: Visual
        right = ttk.LabelFrame(main, text="Визуализация", padding=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(4, 8), pady=8)

        vis_cols = ttk.LabelFrame(right, text="Распределения по столбцам", padding=6)
        vis_cols.pack(fill=tk.BOTH, expand=True)
        self.lb_vis_cols = tk.Listbox(vis_cols, selectmode=tk.EXTENDED, height=10)
        self.lb_vis_cols.pack(fill=tk.BOTH, expand=True)
        ttk.Label(vis_cols, text="Каталог для графиков").pack(anchor="w", pady=(6, 0))
        ttk.Entry(vis_cols, textvariable=self.var_plots_dir).pack(fill=tk.X)
        ttk.Button(vis_cols, text="Сохранить графики", command=self.on_visualize_distributions).pack(pady=6)

        vis_k = ttk.LabelFrame(right, text="Распределение размеров k-групп", padding=6)
        vis_k.pack(fill=tk.X)
        ttk.Label(vis_k, text="top_n").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(vis_k, from_=5, to=200, textvariable=self.var_top_n_vis, width=7).grid(row=0, column=1, sticky="w")
        ttk.Label(vis_k, text="Файл PNG").grid(row=1, column=0, sticky="w")
        ttk.Entry(vis_k, textvariable=self.var_k_plot_path).grid(row=1, column=1, sticky="ew", padx=4)
        vis_k.columnconfigure(1, weight=1)
        ttk.Button(vis_k, text="Построить график k", command=self.on_visualize_k).grid(row=2, column=0, columnspan=2, pady=6)

        # Status bar
        sb = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        sb.pack(side=tk.BOTTOM, fill=tk.X)

        # Disable controls until file loaded
        self._set_controls_state(enabled=False)

    def _set_controls_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        # Iterate through all children and set state when supported
        for widget in self.root.winfo_children():
            self._set_state_recursive(widget, state)

    def _set_state_recursive(self, widget, state):
        # Do not disable top buttons or status
        if isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
            for child in widget.winfo_children():
                self._set_state_recursive(child, state)
            return
        # Skip status and top-level file buttons selection
        if hasattr(widget, "cget"):
            try:
                # Keep top bar file buttons always enabled
                if isinstance(widget, ttk.Button) and widget.cget("text") in ("Открыть Excel", "Сохранить Excel", "Сбросить (перезагрузить)"):
                    widget.configure(state="normal")
                elif isinstance(widget, ttk.Label):
                    pass
                else:
                    widget.configure(state=state)
            except tk.TclError:
                pass

    def _refresh_columns(self):
        if self.df is None:
            return
        cols = list(self.df.columns)

        def set_values(cb, var, extra_default=None):
            cb["values"] = cols
            if var.get() in cols:
                cb.set(var.get())
            elif extra_default and extra_default in cols:
                cb.set(extra_default)
                var.set(extra_default)
            else:
                cb.set("")
                var.set("")

        set_values(self.cb_date_col, self.var_date_col)
        set_values(self.cb_card_col, self.var_card_col, "Карта оплаты")
        set_values(self.cb_pass_col, self.var_pass_col, "Паспортные данные")
        set_values(self.cb_snils_col, self.var_snils_col, "СНИЛС")
        set_values(self.cb_cost_col, self.var_cost_col, "Стоимость анализов")
        set_values(self.cb_doc_col, self.var_doc_col, "Врач")

        self.cb_fam["values"] = cols
        self.cb_name["values"] = cols
        self.cb_otch["values"] = cols

        # Listboxes
        self.var_del_cols.delete(0, tk.END)
        self.lb_qi.delete(0, tk.END)
        self.lb_vis_cols.delete(0, tk.END)
        for c in cols:
            self.var_del_cols.insert(tk.END, c)
            self.lb_qi.insert(tk.END, c)
            self.lb_vis_cols.insert(tk.END, c)

    # ------------------------- File ops -------------------------

    def on_open(self):
        path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel", "*.xlsx"), ("Все файлы", "*.*")]
        )
        if not path:
            return
        try:
            self.status("Загрузка...")
            self.df = pd.read_excel(path)
            self.original_df = self.df.copy()
            self.filepath = path
            self.lbl_file.config(text=f"Файл: {Path(path).name}  |  строк: {len(self.df)}, колонок: {len(self.df.columns)}")
            self._refresh_columns()
            self._set_controls_state(True)
            self.status("Файл загружен.")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
            self.status("Ошибка загрузки.")

    def on_save(self):
        if self.df is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл.")
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Все файлы", "*.*")]
        )
        if not path:
            return
        try:
            self.status("Сохранение...")
            dp.save_current_state(self.df, path)
            self.status(f"Сохранено: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
            self.status("Ошибка сохранения.")

    def on_reset(self):
        if not self.filepath:
            messagebox.showwarning("Нет файла", "Сначала загрузите Excel.")
            return
        try:
            self.status("Перезагрузка...")
            self.df = pd.read_excel(self.filepath)
            self.original_df = self.df.copy()
            self.lbl_file.config(text=f"Файл: {Path(self.filepath).name}  |  строк: {len(self.df)}, колонок: {len(self.df.columns)}")
            self._refresh_columns()
            self.status("Исходные данные восстановлены.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status("Ошибка перезагрузки.")

    # ------------------------- Transforms -------------------------

    def apply_dates(self):
        if not self._check_df(): return
        col = self.var_date_col.get()
        level = self.var_date_level.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку даты.")
            return
        try:
            self.df = dp.decompose_dates(self.df, col, level)
            self._refresh_columns()
            self.status(f"Дата '{col}' → {level}")
        except Exception as e:
            messagebox.showerror("Ошибка обобщения даты", str(e))

    def apply_delete_columns(self):
        if not self._check_df(): return
        idxs = self.var_del_cols.curselection()
        cols = [self.var_del_cols.get(i) for i in idxs]
        if not cols:
            messagebox.showwarning("Выбор", "Выберите колонки.")
            return
        try:
            self.df = dp.delete_columns(self.df, cols)
            self._refresh_columns()
            self.status(f"Удалены колонки: {', '.join(cols)}")
        except Exception as e:
            messagebox.showerror("Ошибка удаления", str(e))

    def apply_decompose_card(self):
        if not self._check_df(): return
        col = self.var_card_col.get()
        element = self.var_card_element.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку карты.")
            return
        try:
            self.df = dp.decompose_bank_card(self.df, col, element)
            self._refresh_columns()
            self.status(f"Карта '{col}' → {element}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_mask_passport(self):
        if not self._check_df(): return
        col = self.var_pass_col.get()
        n = self.var_pass_len.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку паспорта.")
            return
        try:
            self.df = dp.mask_passport_data(self.df, col, n)
            self.status(f"Паспорт '{col}' замаскирован, оставить {n}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_generalize_snils(self):
        if not self._check_df(): return
        col = self.var_snils_col.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку СНИЛС.")
            return
        try:
            self.df = dp.generalize_snils(self.df, col)
            self.status(f"СНИЛС '{col}' обобщен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_fio_to_uid(self):
        if not self._check_df(): return
        s = self.var_fam_col.get() or "Фамилия"
        n = self.var_name_col.get() or "Имя"
        p = self.var_otch_col.get() or "Отчество"
        new = self.var_uid_col.get() or "UID"
        try:
            self.df = dp.combine_fio_to_uid(self.df, s, n, p, new)
            self._refresh_columns()
            self.status(f"UID сформирован в '{new}', ФИО удалены")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_cost_quantiles(self):
        if not self._check_df(): return
        col = self.var_cost_col.get()
        bins = self.var_cost_bins.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку стоимости.")
            return
        try:
            self.df = dp.categorize_costs_quantile(self.df, col, bins)
            self.status(f"Стоимость '{col}' → {bins} квантилей")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_generalize_doctors(self):
        if not self._check_df(): return
        col = self.var_doc_col.get()
        if not col:
            messagebox.showwarning("Выбор", "Выберите колонку врача.")
            return
        try:
            self.df = dp.generalize_doctors_strong(self.df, col)
            self.status(f"Врач '{col}' обобщен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ------------------------- Analytics & suppression -------------------------

    def _selected_qi(self) -> list[str]:
        idxs = self.lb_qi.curselection()
        return [self.lb_qi.get(i) for i in idxs]

    def on_calc_k(self):
        if not self._check_df(): return
        qi = self._selected_qi()
        if not qi:
            messagebox.showwarning("QI", "Выберите квази-идентификаторы.")
            return
        try:
            # Расчет
            group_sizes = self.df.groupby(qi, observed=True).size()
            if group_sizes.empty:
                k = 0
                unique = 0
            else:
                k = int(group_sizes.min())
                unique = int(len(group_sizes))
            # Топ худших групп
            top_n = self.var_top_n_k.get()
            worst = group_sizes.sort_values().head(top_n)

            # Вывод
            self.txt_k.delete("1.0", tk.END)
            self.txt_k.insert(tk.END, f"k-анонимность: {k}\n")
            self.txt_k.insert(tk.END, f"Число групп: {unique}\n\n")
            self.txt_k.insert(tk.END, f"Худшие {min(top_n, len(worst))} групп:\n")
            for val in worst.values:
                self.txt_k.insert(tk.END, f"  k={int(val)}\n")
            self.status(f"k={k}, групп={unique}")
        except Exception as e:
            messagebox.showerror("Ошибка расчета k", str(e))

    def on_suppress(self):
        if not self._check_df(): return
        qi = self._selected_qi()
        if not qi:
            messagebox.showwarning("QI", "Выберите квази-идентификаторы.")
            return
        try:
            if self.var_supp_mode.get() == "frac":
                frac = max(0.0, min(1.0, float(self.var_supp_frac.get())))
                rows_target = int(len(self.df) * frac)
            else:
                rows_target = max(1, int(self.var_supp_rows.get()))
            overshoot = bool(self.var_supp_overshoot.get())

            self.status("Подавление...")
            self.df, report = dp.suppress_worst_k_groups_by_rows(
                self.df, qi, rows_to_remove=rows_target, allow_overshoot=overshoot
            )
            self._refresh_columns()

            # Показать краткий отчет
            self.txt_k.delete("1.0", tk.END)
            self.txt_k.insert(tk.END, "Подавление выполнено\n")
            for k in ("before_k", "after_k", "groups_removed", "rows_removed", "removed_frac"):
                if k in report:
                    self.txt_k.insert(tk.END, f"{k}: {report[k]}\n")
            if "removed_k_hist" in report and not report["removed_k_hist"].empty:
                self.txt_k.insert(tk.END, "\nУдаленные группы по k:\n")
                self.txt_k.insert(tk.END, str(report["removed_k_hist"]))
            self.status(f"Удалено строк: {report.get('rows_removed', 0)}; k: {report.get('before_k','?')} → {report.get('after_k','?')}")
        except Exception as e:
            messagebox.showerror("Ошибка подавления", str(e))

    # ------------------------- Visualization -------------------------

    def on_visualize_distributions(self):
        if not self._check_df(): return
        try:
            idxs = self.lb_vis_cols.curselection()
            cols = [self.lb_vis_cols.get(i) for i in idxs]
            outdir = self.var_plots_dir.get().strip() or "files/plots"
            paths = dp.visualize_distributions(self.df, columns=(cols or None), output_dir=outdir)
            messagebox.showinfo("Готово", f"Сохранено файлов: {len(paths)}\n{outdir}")
            self.status(f"Графики распределений сохранены ({len(paths)})")
        except Exception as e:
            messagebox.showerror("Ошибка визуализации", str(e))

    def on_visualize_k(self):
        if not self._check_df(): return
        qi = self._selected_qi()
        if not qi:
            messagebox.showwarning("QI", "Выберите квази-идентификаторы.")
            return
        try:
            out = self.var_k_plot_path.get().strip() or "files/plots/k_distribution.png"
            top_n = int(self.var_top_n_vis.get())
            path = dp.visualize_k_group_sizes(self.df, qi, output_path=out, top_n=top_n)
            messagebox.showinfo("Готово", f"Сохранено: {path}")
            self.status(f"k-график сохранен: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Ошибка визуализации k", str(e))

    # ------------------------- Utils -------------------------

    def status(self, text: str):
        self.status_var.set(text)
        self.root.update_idletasks()

    def _check_df(self) -> bool:
        if self.df is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите Excel файл.")
            return False
        return True


def main():
    root = tk.Tk()
    app = AnonymizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()