import pandas as pd
import os
import numpy as np
import re

def save_current_state(data: pd.DataFrame, file_path: str):
    # Create a copy to avoid modifying the original DataFrame in memory
    data_to_save = data.copy()

    # Convert datetime columns to the desired string format
    for col in data_to_save.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
        # Check if the column has timezone information
        if getattr(data_to_save[col].dt, 'tz', None) is not None:
            # Format with timezone, adding the colon in the offset
            data_to_save[col] = data_to_save[col].dt.strftime('%Y-%m-%dT%H:%M:%S%z').str.replace(r'(\d{2})$', r':\1', regex=True)
        else:
            # Format naive datetime (without timezone)
            data_to_save[col] = data_to_save[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

    if os.path.exists(file_path):
        os.remove(file_path)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        data_to_save.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass

            adjusted_width = (max_length + 2) * 1.1
            worksheet.column_dimensions[column_letter].width = adjusted_width
def open_from_excel(file_path: str) -> pd.DataFrame:
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        return pd.DataFrame()
    
def fill_numeric_missing_with_mean(df: pd.DataFrame, columns=None, exclude_columns=None) -> pd.DataFrame:
    result_df = df.copy()
    if columns is None:
        columns_to_process = result_df.select_dtypes(include=[np.number]).columns.tolist()
    else:
        columns_to_process = list(columns)
    if exclude_columns is not None:
        columns_to_process = [c for c in columns_to_process if c not in exclude_columns]
    for c in columns_to_process:
        if c in result_df.columns and result_df[c].isnull().any():
            result_df[c] = result_df[c].fillna(result_df[c].mean())
    return result_df

def fill_missing_with_mean_datetime(df: pd.DataFrame, datetime_columns=None, exclude_columns=None, method: str = 'mean') -> pd.DataFrame:
    result_df = df.copy()
    if datetime_columns is None:
        # Используем типы данных DataFrame
        datetime_columns = [c for c in result_df.columns if np.issubdtype(result_df[c].dtype, np.datetime64)]
    else:
        datetime_columns = list(datetime_columns)
    if exclude_columns is not None:
        datetime_columns = [c for c in datetime_columns if c not in exclude_columns]
    for c in datetime_columns:
        if c in result_df.columns:
            series = pd.to_datetime(result_df[c], errors='coerce')
            if series.isnull().any():
                valid = series.dropna()
                if not valid.empty:
                    if method == 'median':
                        fill_value = valid.median()
                    else:
                        fill_value = valid.mean()
                    series = series.fillna(fill_value)
                    result_df[c] = series
    return result_df


def fill_missing_with_mode_card(df: pd.DataFrame, card_columns=None, exclude_columns=None, method: str = 'mode') -> pd.DataFrame:
    result_df = df.copy()
    def is_card(value):
        if pd.isna(value):
            return False
        cleaned = str(value).replace(' ', '')
        return cleaned.isdigit() and len(cleaned) == 16
    if card_columns is None:
        card_columns = []
        for col in result_df.columns:
            sample = result_df[col].dropna().head(10)
            if not sample.empty and sum(is_card(v) for v in sample) >= max(1, len(sample) // 2):
                card_columns.append(col)
    else:
        card_columns = list(card_columns)
    if exclude_columns is not None:
        card_columns = [c for c in card_columns if c not in exclude_columns]
    for col in card_columns:
        if col in result_df.columns and result_df[col].isnull().any():
            valid = result_df[col].dropna()
            if not valid.empty:
                mode_vals = valid.mode()
                fill_value = mode_vals.iloc[0] if not mode_vals.empty else valid.iloc[0]
                result_df[col] = result_df[col].fillna(fill_value)
    return result_df


def fill_missing_with_mode_passport(df: pd.DataFrame, passport_columns=None, exclude_columns=None) -> pd.DataFrame:
    result_df = df.copy()

    def is_passport(value: object) -> bool:
        if pd.isna(value):
            return False
        s = str(value).strip()
        return bool(re.match(r'^\d{2}\s?\d{2}\s?\d{5,7}$', s))

    def normalize_passport(value: object) -> object:
        if pd.isna(value):
            return value
        digits = ''.join(ch for ch in str(value) if ch.isdigit())
        if len(digits) < 10:
            return value  # Не трогаем странные значения
        series1 = digits[:2]
        series2 = digits[2:4]
        number = digits[4:10]  # первые 6 цифр номера
        return f"{series1} {series2} {number}"

    if passport_columns is None:
        passport_columns = []
        for col in result_df.columns:
            sample = result_df[col].dropna().head(10)
            if not sample.empty:
                count = sum(is_passport(v) for v in sample)
                if count >= max(1, len(sample) // 2):
                    passport_columns.append(col)
    else:
        passport_columns = list(passport_columns)
    if exclude_columns is not None:
        passport_columns = [c for c in passport_columns if c not in exclude_columns]

    for col in passport_columns:
        if col not in result_df.columns:
            continue
        # Нормализация существующих значений
        result_df[col] = result_df[col].apply(normalize_passport)
        if result_df[col].isnull().any():
            valid = result_df[col].dropna()
            if not valid.empty:
                mode_vals = valid.mode()
                fill_value = mode_vals.iloc[0] if not mode_vals.empty else valid.iloc[0]
                result_df[col] = result_df[col].fillna(fill_value)
    return result_df


def fill_missing_with_mode_snils(df: pd.DataFrame, snils_columns=None, exclude_columns=None) -> pd.DataFrame:
    result_df = df.copy()

    def is_snils(value: object) -> bool:
        if pd.isna(value):
            return False
        s = str(value).strip()
        return bool(re.match(r'^\d{3}-\d{3}-\d{3}\s\d{2}$', s))

    def normalize_snils(value: object) -> object:
        if pd.isna(value):
            return value
        digits = ''.join(ch for ch in str(value) if ch.isdigit())
        if len(digits) != 11:  # 9 + 2 контрольные
            return value
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:9]} {digits[9:11]}"

    if snils_columns is None:
        snils_columns = []
        for col in result_df.columns:
            sample = result_df[col].dropna().head(10)
            if not sample.empty:
                count = sum(is_snils(v) for v in sample)
                if count >= max(1, len(sample) // 2):
                    snils_columns.append(col)
    else:
        snils_columns = list(snils_columns)
    if exclude_columns is not None:
        snils_columns = [c for c in snils_columns if c not in exclude_columns]

    for col in snils_columns:
        if col not in result_df.columns:
            continue
        result_df[col] = result_df[col].apply(normalize_snils)
        if result_df[col].isnull().any():
            valid = result_df[col].dropna()
            if not valid.empty:
                mode_vals = valid.mode()
                fill_value = mode_vals.iloc[0] if not mode_vals.empty else valid.iloc[0]
                result_df[col] = result_df[col].fillna(fill_value)
    return result_df


def fill_categorical_missing_with_mode(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    result_df = df.copy()
    for col in columns:
        if col in result_df.columns and result_df[col].isnull().any():
            # Убираем пустые строки и NaN, затем находим моду
            valid_values = result_df[col].dropna()
            if not valid_values.empty:
                mode_value = valid_values.mode()
                if not mode_value.empty:
                    fill_value = mode_value.iloc[0]
                    result_df[col] = result_df[col].fillna(fill_value)
    return result_df

def replace_fio_with_gender(df, last_name_col='Фамилия', first_name_col='Имя', patronymic_col='Отчество', 
                          new_gender_col='Пол', delete_original=True):
    """
    Заменяет три столбца ФИО на один столбец 'Пол' с определением пола по отчеству
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Исходный DataFrame
    last_name_col : str, default 'Фамилия'
        Название столбца с фамилиями
    first_name_col : str, default 'Имя'
        Название столбца с именами
    patronymic_col : str, default 'Отчество'
        Название столбца с отчествами
    new_gender_col : str, default 'Пол'
        Название нового столбца с полом
    delete_original : bool, default True
        Удалять ли исходные столбцы ФИО
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame с новым столбцом 'Пол'
    """
    
    # Создаем копию DataFrame чтобы не изменять оригинал
    result_df = df.copy()
    
    def determine_gender_from_patronymic(patronymic):
        """
        Определяет пол по отчеству
        """
        if pd.isna(patronymic) or patronymic == '':
            return 'Неизвестно'
        
        patronymic_str = str(patronymic).strip()
        
        # Женские отчества заканчиваются на 'вна', 'чна', 'шна'
        if patronymic_str.endswith(('вна', 'чна', 'шна')):
            return 'Женский'
        # Мужские отчества заканчиваются на 'вич', 'ьич'
        elif patronymic_str.endswith(('вич', 'ьич')):
            return 'Мужской'
        else:
            return 'Неизвестно'
    
    def determine_gender_from_name(first_name):
        """
        Определяет пол по имени (резервный метод)
        """
        if pd.isna(first_name) or first_name == '':
            return 'Неизвестно'
        
        first_name_str = str(first_name).strip().lower()
        
        # Типичные женские окончания имен
        female_endings = ['а', 'я', 'ия', 'ья', 'на', 'ла', 'ра']
        # Типичные мужские окончания имен  
        male_endings = ['й', 'ь', 'л', 'р', 'н', 'т', 'с', 'в', 'д', 'м']
        
        if any(first_name_str.endswith(ending) for ending in female_endings):
            return 'Женский'
        elif any(first_name_str.endswith(ending) for ending in male_endings):
            return 'Мужской'
        else:
            return 'Неизвестно'
    
    # Проверяем наличие необходимых столбцов
    missing_columns = []
    for col in [last_name_col, first_name_col, patronymic_col]:
        if col not in result_df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"Предупреждение: отсутствуют столбцы: {missing_columns}")
        return result_df
    
    print(f"Обрабатываемые столбцы: {last_name_col}, {first_name_col}, {patronymic_col}")
    print(f"Будет создан столбец: {new_gender_col}")
    
    # Создаем столбец с полом
    genders = []
    
    for idx, row in result_df.iterrows():
        patronymic = row[patronymic_col]
        first_name = row[first_name_col]
        
        # Пробуем определить пол по отчеству
        gender = determine_gender_from_patronymic(patronymic)
        
        # Если по отчеству не определили, пробуем по имени
        if gender == 'Неизвестно':
            gender = determine_gender_from_name(first_name)
        
        genders.append(gender)
    
    # Добавляем новый столбец
    result_df[new_gender_col] = genders
    
    # Удаляем исходные столбцы если нужно
    if delete_original:
        columns_to_drop = [last_name_col, first_name_col, patronymic_col]
        # Удаляем только существующие столбцы
        existing_columns_to_drop = [col for col in columns_to_drop if col in result_df.columns]
        result_df = result_df.drop(columns=existing_columns_to_drop)
        print(f"Удалены столбцы: {existing_columns_to_drop}")
    
    # Статистика
    gender_counts = result_df[new_gender_col].value_counts()
    print(f"\nРаспределение по полу:")
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count} записей")
    
    return result_df




def delete_blocks_random(df, loss_percent=0.1, block_sizes=[(2,2), (3,2), (3,3), (4,2)]):
    data = df.copy()
    n_rows, n_cols = data.shape
    total_cells = n_rows * n_cols
    target_missing = int(total_cells * loss_percent)
    missing = 0

    while missing < target_missing:
        block = block_sizes[np.random.randint(0, len(block_sizes))]
        h, w = block

        i = np.random.randint(0, n_rows - h + 1)
        j = np.random.randint(0, n_cols - w + 1)

        block_mask = data.iloc[i:i+h, j:j+w].isna()
        new_missing = h * w - block_mask.sum().sum()

        data.iloc[i:i+h, j:j+w] = np.nan
        missing += new_missing

    return data
