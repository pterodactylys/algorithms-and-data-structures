from src import methods as m

excel_file = "files/dataset_35k.xlsx"

df = m.open_from_excel(excel_file)
df_full = df.copy()

df = m.delete_blocks(df, block_size=(3, 3), loss_percent=0.1)

df_1 = m.mean_imputation(df)

df_2 = m.linear_regression_imputation(df)

# print("Mean Imputation Relative Error:", m.relative_error(df_full, df_1))
# print("Linear Regression Imputation Relative Error:", m.relative_error(df_full, df_2))