from datetime import date
from pydoc import doc

import pandas as pd
from docxtpl import DocxTemplate

from app.constants import (
    MILITARY_UNIT,
    MILITARY_UNIT_NUMBER,
    TVO_TEXT,
    RelevanceToThePosition,
    StatusPersonal,
    TableHeader,
)
from app.repositories.personnel import ExcelPersonalRepository


class ReportGeneration:
    def __init__(self, repository: ExcelPersonalRepository):
        self.repository = repository

    def generate_report(self, full_name: str) -> dict:
        subordination = self.repository.get_subordination_by_full_name(full_name)

    def get_name_and_surname(self, full_name: str) -> str:
        name_parts = full_name.split(" ")
        return name_parts[1] + " " + name_parts[0]

    def get_text_subordination(self, position_code: str) -> str:
        subordination = self.repository.get_subordination_by_position_code(
            position_code
        )

        result = []

        values = list(subordination.values())
        values.reverse()

        over_list_subordination = [
            {
                "current": values[i]["row"],
                "next": values[i + 1]["row"] if i + 1 < len(values) else None,
            }
            for i in range(len(values))
        ]

        for item in over_list_subordination:
            current_row = item["current"]
            next_row = item["next"]
            next_comander_position = f"Командиру {MILITARY_UNIT}"

            if current_row[TableHeader.STATUS.value] != StatusPersonal.IN_STOCK.value:
                continue

            if (
                next_row is not None
                and next_row[TableHeader.FULL_JOB_TITLE_DATIVE.value]
            ):
                next_comander_position = (
                    next_row[TableHeader.FULL_JOB_TITLE_DATIVE.value].capitalize()
                    + " "
                    + f"військової частини {MILITARY_UNIT_NUMBER}"
                )

            result.append(
                {
                    "full_name": self.get_name_and_surname(
                        current_row[TableHeader.FULL_NAME.value]
                    ),
                    "rank": current_row[TableHeader.RANK.value],
                    "full_job_title": self._get_full_job_title(current_row),
                    "current_position": current_row[
                        TableHeader.FULL_JOB_TITLE_DATIVE.value
                    ].capitalize()
                    + " "
                    + f"військової частини {MILITARY_UNIT_NUMBER}",
                    "next_comander_position": next_comander_position,
                }
            )

        return result

    def _get_full_job_title(self, row: pd.Series) -> str:

        full_job_title = ""
        if (
            row[TableHeader.RELEVANCE_TO_THE_POSITION.value]
            == RelevanceToThePosition.TVO.value
        ):
            full_job_title = (
                TVO_TEXT + " " + row[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]
            )
        else:
            full_job_title = row[TableHeader.FULL_JOB_TITLE.value]

        return full_job_title + " " + f"військової частини {MILITARY_UNIT_NUMBER}"

    def generate_report_over_position(self, tax_id: str) -> list:
        doc = DocxTemplate("C:/Users/chewbaka/Desktop/test_position.docx")

        person = self.repository.get_person_by_tax_id(tax_id)
        subordination = self.get_text_subordination(
            position_code=person[TableHeader.POSITION_CODE.value]
        )
        position = (
            person[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]
            + " "
            + f"військової частини {MILITARY_UNIT_NUMBER}"
        )

        context = {
            "full_name": self.get_name_and_surname(person[TableHeader.FULL_NAME.value]),
            "rank": person[TableHeader.RANK.value],
            "full_job_title": " ",
            "date": date.today().strftime("%d.%m.%Y"),
            "text": f"Дійсним доповідаю, що справи та посаду {position.upper()} здав.",
            "subordination": subordination,
        }

        doc.render(context)
        doc.save("C:/Users/chewbaka/Desktop/result.docx")
