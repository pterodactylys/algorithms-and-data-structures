from statistics import LinearRegression
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def open_from_excel(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    return df

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
            

def relative_error(true, restored):
    mask = ~np.isnan(true)
    return np.mean(np.abs((true[mask] - restored[mask]) / true[mask]))


def delete_blocks(data, block_size=(3, 3), loss_percent=0.1):
    df = data.copy()
    n, m = df.shape
    total_cells = n * m
    target_loss = int(total_cells * loss_percent)
    removed = 0

    while removed < target_loss:
        i = np.random.randint(0, n - block_size[0])
        j = np.random.randint(0, m - block_size[1])
        df.iloc[i:i+block_size[0], j:j+block_size[1]] = np.nan
        removed += block_size[0] * block_size[1]
    return df



def delete_blocks_random(df, loss_percent=0.1, block_sizes=[(2,2), (3,2), (3,3), (4,2)]):
    """
    Удаляет данные блоками случайных размеров, пока не достигнут нужный процент пропусков.

    Параметры:
      df — исходный DataFrame
      loss_percent — доля удаляемых данных (например, 0.1 = 10%)
      block_sizes — возможные размеры блоков (список кортежей)
    """
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



def mean_imputation(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    for column in df.columns:
        if df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(df[column]):
                mean_value = df[column].mean()
                df[column].fillna(mean_value, inplace=True)
            else:
                mode = df[column].mode(dropna=True)
                if not mode.empty:
                    df[column].fillna(mode.iloc[0], inplace=True)
                else:
                    df[column].fillna("", inplace=True)
    return df


def linear_regression_imputation(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    for column in df.columns:
        if not df[column].isnull().any():
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            mode = df[column].mode(dropna=True)
            if not mode.empty:
                df.loc[df[column].isnull(), column] = mode.iloc[0]
            continue

        X_all = df.drop(columns=[column])
        y = df[column]

        X_train = X_all.loc[y.notnull()].copy()
        y_train = y.loc[y.notnull()].astype(float).copy()
        X_pred = X_all.loc[y.isnull()].copy()

        if X_train.empty or X_pred.empty:
            continue

        X_combined = pd.concat([X_train, X_pred], axis=0)
        X_dummies = pd.get_dummies(X_combined, dummy_na=False)
        X_train_enc = X_dummies.iloc[: len(X_train), :].astype(float)
        X_pred_enc = X_dummies.iloc[len(X_train) :, :].astype(float)

        if X_train_enc.shape[1] == 0:
            df.loc[y.isnull(), column] = y_train.mean()
            continue

        try:
            model = LinearRegression()
            model.fit(X_train_enc, y_train)
            preds = model.predict(X_pred_enc)
        except Exception:
            preds = np.full(shape=(len(X_pred_enc),), fill_value=y_train.mean(), dtype=float)

        if pd.api.types.is_integer_dtype(data[column]) or (np.all(np.mod(y_train.dropna(), 1) == 0)):
            preds = np.rint(preds).astype(int)

        df.loc[y.isnull(), column] = preds

    return df
