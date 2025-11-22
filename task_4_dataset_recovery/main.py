"""Основной скрипт для задачи 4: восстановление датасета.

Режимы работы:
1) "preprocess" — заполнение пропусков проверенными методами (средние, моды)
   и сохранение результата в новый Excel.
2) "compare" — экспериментальное сравнение двух методов заполнения
   числовых пропусков: средним значением и линейной регрессией, как
   описано в методических указаниях.
"""

import pandas as pd

import src.methods as methods
import src.comparison as comparison


FILE_PATH = "files/dataset_30k.xlsx"
CHANGED_FILE_PATH = "files/dataset_30k_changed.xlsx"


def run_preprocess() -> None:
    """Базовая обработка датасета и сохранение результата.

    Здесь используются только методы из methods.py, которым ты доверяешь.
    """

    data = methods.open_from_excel(FILE_PATH)

    # Числовые пропуски (например, "Стоимость анализов")
    data = methods.fill_numeric_missing_with_mean(data)

    # Даты визита и готовности анализов
    data = methods.fill_missing_with_mean_datetime(
        data,
        datetime_columns=["Дата посещения врача", "Дата готовности анализов"],
    )

    # Карта оплаты, паспорт, СНИЛС
    data = methods.fill_missing_with_mode_card(data, card_columns=["Карта оплаты"])
    data = methods.fill_missing_with_mode_passport(
        data, passport_columns=["Паспортные данные"]
    )
    data = methods.fill_missing_with_mode_snils(data, snils_columns=["СНИЛС"])

    # Категориальные текстовые столбцы
    data = methods.fill_categorical_missing_with_mode(
        data, ["Анализы", "Симптомы", "Врач"]
    )

    methods.save_current_state(data, CHANGED_FILE_PATH)
    print(f"Результат предобработки сохранён в {CHANGED_FILE_PATH}")


def run_compare(loss_percent: float = 0.1) -> None:
    """Сравнить эффективность двух методов заполнения числовых пропусков.

    Берётся исходный полный датасет (без изменений), формируется подмножество
    полных наблюдений, затем искусственно создаются пропуски и сравниваются
    методы: среднее значение и линейная регрессия с учётом симптомов.
    """

    data = methods.open_from_excel(FILE_PATH)

    # Гарантируем, что "Стоимость анализов" числовая
    if "Стоимость анализов" in data.columns:
        data["Стоимость анализов"] = pd.to_numeric(
            data["Стоимость анализов"], errors="coerce"
        )

    numeric_cols_to_test = ["Стоимость анализов"]
    existing_numeric = [
        col
        for col in numeric_cols_to_test
        if col in data.columns and pd.api.types.is_numeric_dtype(data[col])
    ]

    if not existing_numeric:
        print("Не найден числовой столбец 'Стоимость анализов' для сравнения.")
        return

    comparison.compare_imputation_methods(
        data,
        numeric_cols=existing_numeric,
        loss_percent=loss_percent,
        save_mean_path="files/dataset_30k_mean_imputed.xlsx",
        save_regression_path="files/dataset_30k_regression_imputed.xlsx",
    )


if __name__ == "__main__":
    # Выбери нужный режим: "preprocess" или "compare"
    MODE = "compare"  # или "preprocess"

    if MODE == "preprocess":
        run_preprocess()
    elif MODE == "compare":
        run_compare(loss_percent=0.1)
    else:
        print(f"Неизвестный режим работы: {MODE}")
