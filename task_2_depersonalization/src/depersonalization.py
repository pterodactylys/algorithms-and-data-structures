import pandas as pd
import os

def calculate_k_anonymity_with_stats(df: pd.DataFrame, quasi_identifiers: list[str]) -> dict:
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}") 
    group_sizes = df.groupby(quasi_identifiers).size() 
    k = int(group_sizes.min())
    frequency_distribution = group_sizes.value_counts().sort_index()
    result = {
        "k_anonymity": k,
        "num_groups": len(group_sizes),
        "frequency_distribution": frequency_distribution.to_dict()
    }
    return result

def calculate_k_anonymity_from_df(df: pd.DataFrame, quasi_identifiers: list[str]) -> int:
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")
    group_sizes = df.groupby(quasi_identifiers).size()
    k = group_sizes.min()
    
    return int(k)

def save_current_state(data: pd.DataFrame, file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        data.to_excel(writer, index=False)
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

def delete_columns(data: pd.DataFrame, columns: list) -> pd.DataFrame:
    return data.drop(columns=columns, axis=1)
