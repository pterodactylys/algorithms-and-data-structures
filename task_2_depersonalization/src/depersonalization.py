import pandas as pd
import numpy as np

def calculate_k_anonymity(data: pd.DataFrame, quasi_identifiers: list):
    grouped = data.groupby(quasi_identifiers).size()
    k_anonymity = grouped.min() if not grouped.empty else 0
    
    return {
        "k_anonymity": int(k_anonymity),
        "unique_groups": int(grouped.nunique()),
        "group_sizes": grouped
    }

def detailed_k_anonymity_analysis(data: pd.DataFrame, quasi_identifiers: list):
    result = calculate_k_anonymity(data, quasi_identifiers)
    
    print(f"   K-анонимность: {result['k_anonymity']}")
    print(f"   Уникальных групп: {result['unique_groups']}")
    print(f"   Размеры групп: {result['group_sizes'].to_dict()}")

def masking_data(data: pd.DataFrame, quasi_identifiers: list, begin_len: int, end_len: int):
    for col in quasi_identifiers:
        data[col] = data[col].astype(str).str[:begin_len] + "****" + data[col].astype(str).str[end_len:]
    return data

def generalize_costs_quantile(df, cost_column, quantiles=None, labels=None, replace_original=True):
    """
    Обобщение стоимости анализов на основе квантилей с заменой исходных данных
    
    Parameters:
    df - DataFrame
    cost_column - название столбца со стоимостью
    quantiles - список квантилей [0, 0.25, 0.5, 0.75, 1.0]
    labels - названия категорий
    replace_original - заменять ли исходный столбец (True) или создавать новый (False)
    
    Returns:
    DataFrame с обобщенной стоимостью
    """
    df = df.copy()
    
    if quantiles is None:
        quantiles = [0, 0.25, 0.5, 0.75, 1.0]
    
    if labels is None:
        labels = ['Очень низкая', 'Низкая', 'Средняя', 'Высокая']
    
    cost_values = df[cost_column].dropna()
    bin_edges = [cost_values.quantile(q) for q in quantiles]
    
    bin_edges[-1] = cost_values.max() + 1

    cost_categories = pd.cut(df[cost_column], bins=bin_edges, labels=labels, right=False, include_lowest=True)

    df[cost_column] = cost_categories
    new_column_name = cost_column

    
    return df, bin_edges, labels