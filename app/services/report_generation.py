from dataclasses import asdict, dataclass
from datetime import date
from pydoc import doc

import pandas as pd
from docx import Document
from docxcompose.composer import Composer
from docxtpl import DocxTemplate

from app.exclusion import ReportGenerationExclusion


@dataclass
class Context:
    full_name: str
    rank: str
    full_job_title: str
    date: str
    next_comander_position: str
    text: str
    subordination: list


from io import BytesIO

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
        self.comander_position_dative = f"Командиру {MILITARY_UNIT}"
        self.path_template_report = "C:/Users/chewbaka/Desktop/test_position.docx"
        self.path_save_report = "C:/Users/chewbaka/Desktop/result.docx"

    def get_name_and_surname(self, full_name: str) -> str:
        name_parts = full_name.split(" ")
        return name_parts[1] + " " + name_parts[0]

    def get_text_subordination(self, position_code: str) -> str:
        subordination = self.repository.get_subordination_by_position_code(
            position_code=position_code
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
            next_comander_position = self.comander_position_dative

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

    def _get_context(self, person) -> Context:
        subordination = self.get_text_subordination(
            position_code=person[TableHeader.POSITION_CODE.value]
        )
        next_comander_position = self.comander_position_dative
        if subordination:
            next_comander_position = subordination[0].get("current_position")

        return Context(
            full_name=self.get_name_and_surname(person[TableHeader.FULL_NAME.value]),
            rank=person[TableHeader.RANK.value],
            full_job_title=" ",
            date=date.today().strftime("%d.%m.%Y"),
            next_comander_position=next_comander_position,
            text="",
            subordination=subordination,
        )

    def _generate_document(self, context: Context) -> DocxTemplate:
        doc = DocxTemplate(self.path_template_report)
        doc.render(asdict(context))
        return doc

    def generate_reports(self, contexts: list[Context]) -> None:
        documents = []

        for context in contexts:
            doc = self._generate_document(context)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            documents.append(buffer)

        if not documents:
            raise ReportGenerationExclusion(
                "Рапорт не був згенерований, данні для генерації відсутні!!!"
            )

        master = Document(documents[0])
        composer = Composer(master)

        for buffer in documents[1:]:
            master.add_page_break()

            composer.append(Document(buffer))

        composer.save(self.path_save_report)

        for buffer in documents:
            buffer.close()

    def get_context_report_over_position(self, tax_id: str):
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(person=person)
        position = (
            person[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]
            + " "
            + f"військової частини {MILITARY_UNIT_NUMBER}"
        )
        context.text = (
            f"Дійсним доповідаю, що справи та посаду {position.upper()} здав."
        )
        return context
