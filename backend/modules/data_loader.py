import pandas as pd

ENCODINGS = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1', 'utf-16']

def load_dataset(path: str) -> pd.DataFrame:
    path_lower = path.lower()

    # ── CSV / TSV / TXT ──────────────────────────────────
    if path_lower.endswith(('.csv', '.tsv', '.txt')):
        # Try common delimiters automatically
        for sep in [',', '\t', ';', '|']:
            for enc in ENCODINGS:
                try:
                    df = pd.read_csv(path, sep=sep, encoding=enc, on_bad_lines='skip')
                    if df.shape[1] > 1:   # at least 2 columns → correct delimiter
                        return df
                except Exception:
                    continue
        raise ValueError("Could not read CSV/TSV file with any known encoding or delimiter.")

    # ── Excel ────────────────────────────────────────────
    elif path_lower.endswith(('.xlsx', '.xls')):
        return pd.read_excel(path)

    # ── JSON ─────────────────────────────────────────────
    elif path_lower.endswith('.json'):
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)   # newline-delimited JSON

    # ── Parquet ──────────────────────────────────────────
    elif path_lower.endswith('.parquet'):
        return pd.read_parquet(path)

    # ── ODS (OpenOffice Spreadsheet) ─────────────────────
    elif path_lower.endswith('.ods'):
        return pd.read_excel(path, engine='odf')

    else:
        raise ValueError(
            f"Unsupported file type. Accepted: .csv, .tsv, .txt, .xlsx, .xls, .json, .parquet, .ods"
        )