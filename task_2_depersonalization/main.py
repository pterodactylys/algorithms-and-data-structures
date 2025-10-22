import pandas as pd
from pathlib import Path
from src import depersonalization as dp

filepath = "files/dataset_100k.xlsx"


df = pd.read_excel(filepath)
df = dp.decompose_dates(df, 'Дата посещения врача', 'Квартал')
df = dp.delete_columns(df, ['Дата готовности анализов'])
df = dp.decompose_bank_card(df, 'Карта оплаты', 'Платежная система')
df = dp.mask_passport_data(df, 'Паспортные данные', 1)
df = dp.generalize_snils(df, 'СНИЛС')

# df = dp.map_symptoms_to_systems_replace(df, 'Симптомы', dp.organ_systems)
# df = dp.map_tests_to_systems_replace(df, 'Анализы', dp.tests_by_organ_system)
# df = dp.unify_medical_columns(df, 'Симптомы', 'Врач', 'Анализы', dp.organ_systems, dp.tests_by_organ_system)
df = dp.combine_fio_to_uid(df, 'Фамилия', 'Имя', 'Отчество')
df = dp.categorize_costs_quantile(df, 'Стоимость анализов', 3)
df = dp.generalize_doctors_strong(df, 'Врач')
df["Симптомы"] = df["Врач"]
df["Анализы"] = df["Врач"]

df, rep = dp.suppress_worst_k_groups_by_rows(df, ['Паспортные данные', 'СНИЛС', 
         'Дата посещения врача', 'Стоимость анализов', 'Врач',
        'Платежная система'], len(df) * 0.03)
print(rep)

print(dp.calculate_k_anonymity_from_df_debug(df, ['Паспортные данные', 'СНИЛС', 
         'Дата посещения врача', 'Стоимость анализов', 'Врач',
        'Платежная система']))

print(dp.worst_k_anonymity_groups(df, ['Паспортные данные', 'СНИЛС', 
         'Дата посещения врача', 'Стоимость анализов', 'Врач',
        'Платежная система'], n=10))

print(dp.visualize_distributions(df, ['Паспортные данные', 'СНИЛС', 
         'Дата посещения врача', 'Стоимость анализов', 'Врач',
        'Платежная система']))

print(dp.visualize_k_group_sizes(df, ['Паспортные данные', 'СНИЛС', 
         'Дата посещения врача', 'Стоимость анализов', 'Врач',
        'Платежная система'], top_n=100))


# dp.copy_and_save_current_state(df)



