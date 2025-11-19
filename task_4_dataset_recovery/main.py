import src.methods as methods

file_path = "files/dataset_30k.xlsx"

changed_file_path = "files/dataset_30k_changed.xlsx"

data = methods.open_from_excel(changed_file_path)
# data = methods.replace_fio_with_gender(data)
# data = methods.delete_blocks_random(data, loss_percent=0.1)
data = methods.fill_numeric_missing_with_mean(data)
data = methods.fill_missing_with_mean_datetime(data, datetime_columns=['Дата посещения врача', 'Дата готовности анализов'])
data = methods.fill_missing_with_mode_card(data, card_columns=['Карта оплаты'])
data = methods.fill_missing_with_mode_passport(data, passport_columns=['Паспортные данные'])
data = methods.fill_missing_with_mode_snils(data, snils_columns=['СНИЛС'])
data = methods.fill_categorical_missing_with_mode(data, ['Анализы', 'Симптомы', 'Пол'])
methods.save_current_state(data, changed_file_path)