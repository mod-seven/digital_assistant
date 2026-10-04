from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from app.database.connection import init_database
from app.repositories.personnel import PandasExcelPersonnelRepository
from app.repositories.signatures import SignaturesRepository


@dataclass
class AppState:
    file_path: Path | None = None
    file_name: str | None = None

    sheets: dict[str, pd.DataFrame] = field(default_factory=dict)
    df: pd.DataFrame | None = None

    imported: bool = False

    personnel_repository: PandasExcelPersonnelRepository | None = None

    # init_database()

    signatures_repository = SignaturesRepository()

    _number_of_staff_positions: int | None = None
    _number_on_the_list: int | None = None
    _number_row: int | None = None

    @property
    def number_of_staff_positions(self) -> int:
        if self._number_of_staff_positions is None:
            if self.personnel_repository:
                self._number_of_staff_positions = (
                    self.personnel_repository.get_number_of_staff_positions()
                )

        return self._number_of_staff_positions or 0

    @property
    def number_on_the_list(self) -> int:
        if self._number_on_the_list is None:
            if self.personnel_repository:
                self._number_on_the_list = (
                    self.personnel_repository.get_number_on_the_list()
                )

        return self._number_on_the_list or 0

    @property
    def number_row(self) -> int:
        if self._number_row is None:
            if self.df is not None:
                self._number_row = len(self.df)

        return self._number_row or 0
