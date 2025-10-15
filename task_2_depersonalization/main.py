from src import depersonalization as dp
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# file_path = Path("files") / "dataset_5k.xlsx"
file_path = "files/dataset_100k.xlsx"
df = pd.read_excel(file_path)

# df = dp.delete_columns(df, ['Имя', 'Отчество', 'Анализы', 'Врач', 'Дата готовности анализов', 'СНИЛС'])
# df = dp.microaggregation_of_datas(df, 'Дата посещения врача', True)
# df = dp.masking_data(df, ['Карта оплаты'], 1, 50)
# # df = dp.masking_data(df, ['СНИЛС'], 1, 50)
# df = dp.generalize_passport_data(df, 'Паспортные данные')
# df = dp.generalize_symptoms(df, 'Симптомы', True)
# df, bins, labels = dp.generalize_costs_quantile(df, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
# df = dp.pseudoname(df, 'Фамилия')
# dp.detailed_k_anonymity_analysis(df, ['Паспортные данные', 'Симптомы', 'Дата посещения врача', 'Стоимость анализов'])
# print(dp.top_bad_k_anonymities(df, ['Паспортные данные', 'Симптомы', 'Дата посещения врача', 'Стоимость анализов'], 100))
# df = dp.save_current_state(df, "files/dataset_100k_depersonalized.xlsx")
def apply_functions(selected_functions):
    df_local = pd.read_excel(file_path)
    if 'Delete Columns' in selected_functions:
        df_local = dp.delete_columns(df_local, ['Имя', 'Отчество', 'Анализы', 'Врач', 'Дата готовности анализов', 'СНИЛС'])
    if 'Microaggregation' in selected_functions:
        df_local = dp.microaggregation_of_datas(df_local, 'Дата посещения врача', True)
    if 'Masking' in selected_functions:
        df_local = dp.masking_data(df_local, ['Карта оплаты'], 1, 50)
    if 'Generalize Passport' in selected_functions:
        df_local = dp.generalize_passport_data(df_local, 'Паспортные данные')
    if 'Generalize Symptoms' in selected_functions:
        df_local = dp.generalize_symptoms(df_local, 'Симптомы', True)
    if 'Generalize Costs' in selected_functions:
        df_local, bins, labels = dp.generalize_costs_quantile(df_local, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
    if 'Pseudoname' in selected_functions:
        df_local = dp.pseudoname(df_local, 'Фамилия')
    messagebox.showinfo("Info", "Selected functions applied.")
    return df_local

def show_k_anonymity():
    # df_local = pd.read_excel(file_path)
    # df_local = dp.delete_columns(df_local, ['Имя', 'Отчество', 'Анализы', 'Врач', 'Дата готовности анализов', 'СНИЛС'])
    # df_local = dp.microaggregation_of_datas(df_local, 'Дата посещения врача', True)
    # df_local = dp.masking_data(df_local, ['Карта оплаты'], 1, 50)
    # df_local = dp.generalize_passport_data(df_local, 'Паспортные данные')
    # df_local = dp.generalize_symptoms(df_local, 'Симптомы', True)
    # df_local, bins, labels = dp.generalize_costs_quantile(df_local, 'Стоимость анализов', [0, 0.25, 0.5, 0.75, 1.0])
    # df_local = dp.pseudoname(df_local, 'Фамилия')
    info = dp.top_bad_k_anonymities(df_local, ['Паспортные данные', 'Симптомы', 'Дата посещения врача', 'Стоимость анализов'], 100)
    messagebox.showinfo("K-Anonymity Info", str(info))

root = tk.Tk()
root.title("Depersonalization Functions")

functions = [
    'Delete Columns',
    'Microaggregation',
    'Masking',
    'Generalize Passport',
    'Generalize Symptoms',
    'Generalize Costs',
    'Pseudoname'
]

vars = []
for func in functions:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(root, text=func, variable=var)
    chk.pack(anchor='w')
    vars.append(var)

def on_apply():
    selected = [f for f, v in zip(functions, vars) if v.get()]
    df_result = apply_functions(selected)
    dp.save_current_state(df_result, "files/dataset_100k_depersonalized.xlsx")

apply_btn = tk.Button(root, text="Apply Selected Functions", command=on_apply)
apply_btn.pack(pady=10)

k_anonymity_btn = tk.Button(root, text="Show K-Anonymity Info", command=show_k_anonymity)
k_anonymity_btn.pack(pady=10)

root.mainloop()
