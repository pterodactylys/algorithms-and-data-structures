import pandas as pd
from pathlib import Path
from src import depersonalization as dp

filepath = "files/dataset_100k_depersonalized.xlsx"

df = pd.read_excel(filepath)
print(dp.calculate_k_anonymity_with_stats(df, ['Паспортные данные', 'Симптомы', 'Дата посещения врача',
    'Стоимость анализов', 'Карта оплаты']))
