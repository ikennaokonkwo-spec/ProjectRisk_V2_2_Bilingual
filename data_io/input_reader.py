from __future__ import annotations
import pandas as pd
from localization.schema import canonical_header, resolve_sheets, normalize_table, SHEETS

REQUIRED_SHEETS = ["Project", "Activities", "Risk_Register", "Risk_Activity_Map"]
HEADER_KEYS = {
    "Project": {"Field", "Value"},
    "Activities": {"Activity_ID", "Duration_Model"},
    "Risk_Register": {"Risk_ID", "Risk_Type", "Probability"},
    "Risk_Activity_Map": {"Risk_ID", "Activity_ID", "Impact_Type", "Distribution"},
    "Risk_Relationships": {"Parent_Risk", "Child_Risk"},
    "Risk_Treatments": {"Risk_ID", "Treated_Probability"},
    "Risk_Categories": {"Category", "Definition"},
    "Case_Assumptions": {"Activity_ID", "Original_Base_Cost", "Time_Dependent_Share"},
}

def _header(value):
    return "" if pd.isna(value) else canonical_header(value)

def _read_table(path, sheet: str, header_row: int | None = None, canonical_sheet: str | None = None) -> pd.DataFrame:
    """Detect each table independently; title/blank rows and fonts are immaterial."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    required = HEADER_KEYS[canonical_sheet or sheet]
    if header_row is None:
        matches = [i for i, row in raw.head(50).iterrows()
                   if required.issubset({_header(v) for v in row})]
        if not matches:
            raise ValueError(f"Worksheet '{sheet}': could not locate a header row in the first 50 rows. "
                             f"Required headers: {', '.join(sorted(required))}.")
        if len(matches) > 1:
            raise ValueError(f"Worksheet '{sheet}': multiple header rows found; keep one table header.")
        header_row = matches[0]
    headers = [_header(v) for v in raw.iloc[header_row]]
    populated = [h for h in headers if h]
    if len(populated) != len(set(populated)):
        raise ValueError(f"Worksheet '{sheet}': duplicate column names in header row {header_row+1}.")
    df = raw.iloc[header_row+1:].copy()
    df.columns = [h or f"Unnamed: {i}" for i, h in enumerate(headers)]
    return df.dropna(how="all").reset_index(drop=True)

def read_v1_workbook(path: str) -> dict[str, pd.DataFrame]:
    with pd.ExcelFile(path) as book:
        resolved = resolve_sheets(book.sheet_names)
        missing = [s for s in REQUIRED_SHEETS if s not in resolved]
        if missing:
            raise ValueError("Missing required worksheet(s): " + ", ".join(missing))
        data = {}
        for canonical, actual in resolved.items():
            df = _read_table(book, actual, canonical_sheet=canonical)
            # Infer text-number convention from sheet name or translated headers.
            raw = pd.read_excel(book, sheet_name=actual, header=None, nrows=50)
            pt = actual != canonical or any(
                isinstance(v,str) and canonical_header(v) != v.strip()
                for row in raw.values for v in row
                if isinstance(v,str) and canonical_header(v) in HEADER_KEYS[canonical]
            )
            if canonical == "Project":
                df = df[["Field", "Value"]].dropna(subset=["Field"]).copy()
                df["Field"] = df["Field"].astype(str).str.strip()
            data[canonical] = normalize_table(df, canonical, pt)
        return data

def project_settings(project_df: pd.DataFrame) -> dict:
    return dict(zip(project_df["Field"], project_df["Value"]))
