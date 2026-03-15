import pandas as pd

def load_dataset(path):
    if path.endswith(".csv"):
        try:
            df = pd.read_csv(path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(path, encoding='latin1')
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding='cp1252')
    elif path.endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type")
    return df