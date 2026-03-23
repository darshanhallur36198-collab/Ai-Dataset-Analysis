import pandas as pd

ENCODINGS = ["utf-8", "latin1", "cp1252", "iso-8859-1", "utf-16"]


def load_dataset(path: str) -> pd.DataFrame:
    path_lower = path.lower()

    if path_lower.endswith((".csv", ".tsv", ".txt")):
        # Try common delimiters and encodings.
        for sep in [",", "\t", ";", "|"]:
            for enc in ENCODINGS:
                try:
                    df = pd.read_csv(path, sep=sep, encoding=enc, on_bad_lines="skip")
                    if df.shape[1] > 1:
                        return df
                except Exception:
                    continue
        raise ValueError("Could not read CSV/TSV file with any known encoding or delimiter.")

    elif path_lower.endswith((".xlsx", ".xlsm", ".xltx", ".xltm")):
        try:
            return pd.read_excel(path, engine="openpyxl")
        except ImportError as exc:
            raise ValueError(
                "Excel support for .xlsx files is not installed. Install openpyxl: `pip install openpyxl`."
            ) from exc

    elif path_lower.endswith(".xls"):
        try:
            return pd.read_excel(path, engine="xlrd")
        except ImportError as exc:
            raise ValueError(
                "Excel support for .xls files is not installed. Install xlrd: `pip install xlrd`."
            ) from exc

    elif path_lower.endswith(".json"):
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)

    elif path_lower.endswith(".parquet"):
        return pd.read_parquet(path)

    elif path_lower.endswith(".ods"):
        try:
            return pd.read_excel(path, engine="odf")
        except ImportError as exc:
            raise ValueError(
                "ODS support is not installed. Install odfpy: `pip install odfpy`."
            ) from exc

    else:
        raise ValueError(
            "Unsupported file type. Accepted: .csv, .tsv, .txt, .xlsx, .xls, .json, .parquet, .ods"
        )
