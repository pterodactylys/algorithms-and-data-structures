from src import depersonalization as dp
import pandas as pd
from pathlib import Path

file_path = Path("files") / "dataset_100k.xlsx"
df = pd.read_excel(file_path)
print(dp.calculate_k_anonymity(df, ['Фамилия', 'Врач']))