import csv_controller
import pandas as pd
from csv_controller import select_columns
from utils import split_and_convert_iso_datetime

csv = csv_controller.load_csv_file()
# print(csv.head())
# print(csv.columns)

selected_cols = select_columns(csv)
# print(selected_cols.head())

# edited_cols = selected_cols.loc[:, ["Formatted Date", "Formatted Time"]] = selected_cols['Date'].apply(
#     lambda x: pd.Series(split_and_convert_iso_datetime(x))
# )
# print(edited_cols.head())