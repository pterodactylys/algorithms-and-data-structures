import pandas as pd
import os
import numpy as np
import re

def save_current_state(data: pd.DataFrame, file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
    # Minimal save (engine selection left to pandas)
    data.to_excel(file_path, index=False)

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