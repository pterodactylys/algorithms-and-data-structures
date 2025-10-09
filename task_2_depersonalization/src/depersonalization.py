import pandas as pd

def calculate_k_anonymity(data: pd.DataFrame, quasi_identifiers: list):
    grouped = data.groupby(quasi_identifiers).size()
    return grouped
