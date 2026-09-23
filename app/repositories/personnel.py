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
    def get_subordination_by_position_code(self, position_code: str) -> list: ...

    @abstractmethod
    def get_colomans_position(self, count: int) -> list: ...


class PandasExcelPersonnelRepository(ExcelPersonalRepository):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_number_of_staff_positions(self) -> int:
        return self.df[TableHeader.POSITION_CODE].nunique()

    def get_number_on_the_list(self) -> int:
        return self.df[TableHeader.FULL_NAME].nunique()

    def get_colomans_position(self, count: int) -> list:
        unit_index = self.df.columns.get_loc(TableHeader.UNIT.value)
        return self.df.columns[unit_index : unit_index + count]

    def get_person_by_tax_id(self, tax_id: str) -> dict:
        rows = self.df[self.df[TableHeader.TAX_ID] == tax_id]

        if rows.empty:
            raise ExcelPersonalRepositoryExclusion(
                f"Не знайдено запису з РНОКПП (ІПН): {tax_id}"
            )
        return rows.iloc[0].to_dict()

    def get_subordination_by_position_code(self, position_code: str) -> dict:
        rows = self.df[self.df[TableHeader.POSITION_CODE] == position_code]

        if rows.empty:
            raise ExcelPersonalRepositoryExclusion(
                f"Не знайдено запису з кодом посади: {position_code}"
            )
        row = rows.iloc[0]

        subordination_columns = self.get_colomans_position(3)

        subordination = [
            row[column] for column in subordination_columns if pd.notna(row[column])
        ]

        filtered_df = self.df[self.df[subordination_columns[0]] == subordination[0]]

        heads = {}

        for column in subordination_columns:
            first_rows = filtered_df[filtered_df[column].notna()].drop_duplicates(
                column, keep="first"
            )

            for _, head_row in first_rows.iterrows():
                unit = head_row[column]

                if (
                    pd.notna(unit)
                    and unit in subordination
                    and unit not in heads
                    and position_code != head_row[TableHeader.POSITION_CODE]
                ):
                    heads[unit] = {
                        TableHeader.FULL_NAME.value: head_row[TableHeader.FULL_NAME],
                        "row": head_row,
                    }

        return heads
