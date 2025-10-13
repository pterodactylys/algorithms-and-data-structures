from src import depersonalization as dp
import pandas as pd
from pathlib import Path

file_path = Path("files") / "dataset_50k.xlsx"
df = pd.read_excel(file_path)
# df = dp.masking_data(df, ['Карта оплаты'], 4, 50)
df, bins, labels = dp.generalize_costs_quantile(df, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
dp.detailed_k_anonymity_analysis(df, ['Стоимость анализов'])

    