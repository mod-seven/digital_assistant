from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from app.repositories.personnel import PandasExcelPersonnelRepository

dataclass


class AppState:
    file_path: Path | None = None
    file_name: str | None = None

    sheets: dict[str, pd.DataFrame] = field(default_factory=dict)
    df: pd.DataFrame | None = None

    imported: bool = False

    personnel_repository: PandasExcelPersonnelRepository | None = None
