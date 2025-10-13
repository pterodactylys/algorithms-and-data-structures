from src import depersonalization as dp
import pandas as pd
from pathlib import Path

file_path = Path("files") / "dataset_100k.xlsx"
df = pd.read_excel(file_path)

# df, bins, labels = dp.generalize_costs_quantile(df, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
# df = dp.generalize_symptoms(df, 'Симптомы')
df = dp.microaggregation_of_datas(df, 'Дата посещения врача')
df = dp.microaggregation_of_datas(df, 'Дата готовности анализов')
df = dp.masking_data(df, ['Карта оплаты'], 1, 50)
df = dp.masking_data(df, ['СНИЛС'], 1, 50)
df = dp.generalize_passport_data(df, 'Паспортные данные')
df = dp.generalize_symptoms(df, 'Симптомы')
df = dp.encrypt_name(df, 'Фамилия')
dp.detailed_k_anonymity_analysis(df, ['Дата посещения врача', 'Симптомы', 'Паспортные данные', 'Карта оплаты', 'Фамилия'])
    