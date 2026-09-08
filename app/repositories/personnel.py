from abc import ABC, abstractmethod

import pandas as pd

from app.constants import TableHeader
from app.exclusion import ExcelPersonalRepositoryExclusion


class ExcelPersonalRepository(ABC):
    @abstractmethod
    def get_number_of_staff_positions(self) -> int: ...

    @abstractmethod
    def get_number_on_the_list(self) -> int: ...

    @abstractmethod
    def get_subordination_by_full_name(self, full_name: str) -> dict: ...


class PandasExcelPersonnelRepository(ExcelPersonalRepository):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_number_of_staff_positions(self) -> int:
        return self.df[TableHeader.POSITION_CODE].nunique()

    def get_number_on_the_list(self) -> int:
        return self.df[TableHeader.FULL_NAME].nunique()

    def get_subordination_by_full_name(self, full_name: str) -> dict:
        rows = self.df[self.df[TableHeader.FULL_NAME] == full_name]

        if rows.empty:
            raise ExcelPersonalRepositoryExclusion(
                f"Не знайдено запису з ПІБ: {full_name}"
            )
        row = rows.iloc[0]

        unit_index = self.df.columns.get_loc(TableHeader.UNIT)

        subordination_columns = self.df.columns[unit_index : unit_index + 3]

        subordination = [
            row[column] for column in subordination_columns if pd.notna(row[column])
        ]

        heads = {}

        for column in subordination_columns:
            first_rows = self.df[self.df[column].notna()].drop_duplicates(
                column, keep="first"
            )

            for _, head_row in first_rows.iterrows():
                unit = head_row[column]

                if unit in subordination:

                    if (
                        pd.notna(unit)
                        and unit not in heads
                        and full_name != head_row[TableHeader.FULL_NAME]
                    ):
                        heads[unit] = {
                            TableHeader.FULL_NAME.value: head_row[
                                TableHeader.FULL_NAME
                            ],
                            TableHeader.ROW_NUMBER.value: head_row[
                                TableHeader.ROW_NUMBER
                            ],
                            TableHeader.POSITION_CODE.value: head_row[
                                TableHeader.POSITION_CODE
                            ],
                        }
        return heads
