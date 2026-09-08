from pathlib import Path

import pandas as pd

from app.constants import TableHeader
from app.exclusion import ImportExcelExclusion
from app.state import AppState


def import_excel(file_path, state: AppState):
    try:
        path = Path(file_path)

        sheets = pd.read_excel(
            path,
            sheet_name=None,
            engine="openpyxl",
        )

        sheet_name, df = next(iter(sheets.items()))

        required_headers = {header.value for header in TableHeader}

        missing_headers = required_headers - set(df.columns)

        if missing_headers:
            raise ImportExcelExclusion(
                f"Відсутні обов'язкові заголовки у файлі {path.name}: "
                f"{', '.join(missing_headers)}"
            )

        state.file_path = path
        state.file_name = path.name
        state.sheets = sheets
        state.df = df
        state.imported = True

    except Exception as error:
        raise ImportExcelExclusion(f"Помилка імпорту: {error}")
