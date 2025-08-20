import pandas as pd

def export_to_excel(df, filename="export.xlsx"):
    df.to_excel(filename, index=False)
    return filename
