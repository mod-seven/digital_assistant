from dataclasses import asdict, dataclass
from datetime import date, datetime
from pydoc import doc

import pandas as pd
from docx import Document
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, RichText
from shevchenko import GrammaticalCase

from app.exclusion import ReportGenerationExclusion
from app.services.ukrainian_declension import get_shevchenko_result
from app.settings import TEMPLATE_REPORT_PATH
from app.utils import format_date_ukrainian, format_day_text, number_to_words_ua


@dataclass
class Context:
    full_name: str
    rank: str
    full_name_genitsve: str
    rank_genitsve: str
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
    WORD_FONT,
    WORD_SIZE,
    RelevanceToThePosition,
    ReportType,
    StatusPersonal,
    TableHeader,
)
from app.repositories.personnel import ExcelPersonalRepository


class ReportGeneration:
    def __init__(self, repository: ExcelPersonalRepository, path_save_report: str):
        self.repository = repository
        self.comander_position_dative = f"Командиру {MILITARY_UNIT}"
        self.path_template_report = TEMPLATE_REPORT_PATH
        self.path_save_report = path_save_report

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

    def _get_context(
        self,
        person,
        date,
        position_code: str | None = None,
    ) -> Context:
        position_code = (
            position_code if position_code else person[TableHeader.POSITION_CODE.value]
        )
        subordination = self.get_text_subordination(position_code=position_code)
        next_comander_position = self.comander_position_dative
        if subordination:
            next_comander_position = subordination[0].get("current_position")

        full_name = self.get_name_and_surname(person[TableHeader.FULL_NAME.value])
        full_name_split = full_name.split(" ")
        rank = person[TableHeader.RANK.value]

        result_shevchenko = get_shevchenko_result(
            grammatacal_case=GrammaticalCase.GENITIVE,
            gender=person[TableHeader.GENDER.value],
            given_name=full_name_split[0],
            family_name=full_name_split[1],
            military_rank=rank,
        )

        return Context(
            full_name=full_name,
            rank=rank,
            full_name_genitsve=f"{result_shevchenko.get('givenName')} {result_shevchenko.get('familyName')}",
            rank_genitsve=result_shevchenko.get("militaryRank"),
            full_job_title=self._get_full_job_title(person),
            date=date,
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

    def get_context_report_over_position(
        self,
        tax_id: str,
        date_raport: str = date.today().strftime("%d.%m.%Y"),
    ) -> Context:
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(person=person, date=date_raport)

        position = (
            person[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]
            + " "
            + f"військової частини {MILITARY_UNIT_NUMBER}"
        )

        rt = RichText()
        rt.add(
            f"Дійсним доповідаю, що справи та посаду {position.upper()} здав.",
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        context.full_job_title = " "
        context.text = rt

        return context

    def get_context_report_accepted_position(
        self,
        position_code: str,
        tax_id: str,
        order_name: str,
        oder_number: str,
        oder_date: str,
        date_raport: str = date.today().strftime("%d.%m.%Y"),
    ) -> Context:
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(
            person=person,
            position_code=position_code,
            date=date_raport,
        )
        row = self.repository.get_row_by_position_code(position_code=position_code)

        order = f"{order_name} від {format_date_ukrainian(datetime.strptime(oder_date, '%d.%m.%Y'))} №{oder_number}"
        position = (
            row[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]
            + " "
            + f"військової частини {MILITARY_UNIT_NUMBER}"
        )
        data_accepted = format_date_ukrainian(
            datetime.strptime(date_raport, "%d.%m.%Y")
        )

        rt = RichText()
        rt.add(
            f"Доповідаю, що відповідно до наказу {order} призначений на посаду {position.upper()}.",
            font=WORD_FONT,
            size=WORD_SIZE,
        )
        rt.add("\n\t")
        rt.add(
            f"Справи та посаду {position.upper()}, з {data_accepted} прийняв та приступив до виконання обов’язків за посадою.",
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        context.full_job_title = ""
        context.text = rt
        return context

    def get_contexts(self, file_data: dict) -> list[Context]:
        contexts = []
        for method, items in file_data.items():
            for item in items:
                if ReportType.REPORT_OVER_POSITION.name == method:
                    context = self.get_context_report_over_position(**item)
                elif ReportType.REPORT_ACCEPTED_POSITION.name == method:
                    context = self.get_context_report_accepted_position(**item)
                contexts.append(context)

        return contexts

    def get_context_ozdorovlennya(
        self,
        tax_id: str,
        year: str = date.today().strftime("%Y"),
        date_raport: str = date.today().strftime("%d.%m.%Y"),
    ) -> Context:
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(person=person, date=date_raport)

        text = (
            "У відповідності до розділу до XXІІІ “Порядку виплати грошового забезпечення військовослужбовцям "
            "Збройних сил України та деяким іншим особам”, затвердженого наказом Міністерства оборони "
            "України від 07.06.2018 № 260, прошу Вашого клопотання перед вищим командуванням про виплату "
            f"мені грошової допомоги на оздоровлення за {year} рік."
        )

        rt = RichText()
        rt.add(
            text,
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        context.text = rt
        return context

    def get_shhorichnu_vidpustku(
        self,
        tax_id: str,
        days: int,
        roud_days: str | None,
        tvo_tax_id: str | None,
        adress: str,
        phone: str,
        star_data: str,
        year: str = date.today().strftime("%Y"),
        date_raport: str = date.today().strftime("%d.%m.%Y"),
    ) -> Context:
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(person=person, date=date_raport)

        rt = RichText()
        rt.add(
            (
                f"Прошу Вашого дозволу про надання мені частини щорічної основної відпустки, за {year} рік, "
                f"терміном на {days} ({number_to_words_ua(days)}) календарних днів з {star_data} року."
            ),
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        if roud_days:
            roud_days = int(roud_days)
            rt.add("\n\t")
            rt.add(
                (
                    f"Прошу надати час, необхідний для проїзду в межах України до місця проведення "
                    f"відпустки та назад у кількості {roud_days} {format_day_text(roud_days)}."
                ),
                font=WORD_FONT,
                size=WORD_SIZE,
            )

        rt.add("\n\t")
        rt.add(
            (
                "З правилами поведінки в громадських місцях, забороною вживання алкогольних та наркотичних "
                "речовин під час проведення відпустки ознайомлений та зобов’язуюсь їх виконувати. Зобов’язуюсь повернутись вчасно."
            ),
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        if tvo_tax_id:
            tvo_person = self.repository.get_person_by_tax_id(tvo_tax_id)
            full_name = tvo_person[TableHeader.FULL_NAME.value].split(" ")

            result_shevchenko = get_shevchenko_result(
                grammatacal_case=GrammaticalCase.ACCUSATIVE,
                gender=tvo_person[TableHeader.GENDER.value],
                given_name=full_name[1],
                patronymic_name=full_name[2],
                family_name=full_name[0],
                military_rank=tvo_person[TableHeader.RANK.value],
            )
            rt.add("\n\t")
            rt.add(
                (
                    f"Тимчасове виконання обов’язків прошу покласти на: {tvo_person[TableHeader.FULL_JOB_TITLE_ACCUSATIVE.value]} {result_shevchenko.get('militaryRank')} "
                    f"{result_shevchenko.get('familyName')} {result_shevchenko.get('givenName')} {result_shevchenko.get('patronymicName')}."
                ),
                font=WORD_FONT,
                size=WORD_SIZE,
            )

        rt.add("\n\t")
        rt.add(
            f"Відпустку буду проводити за адресою: {adress}.",
            font=WORD_FONT,
            size=WORD_SIZE,
        )
        rt.add("\n\t")
        rt.add(
            f"Телефон: {phone}.",
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        context.text = rt
        return context

    def get_context_free_theme(
        self,
        tax_id: str,
        date_raport: str = date.today().strftime("%d.%m.%Y"),
    ) -> Context:
        person = self.repository.get_person_by_tax_id(tax_id)
        context = self._get_context(person=person, date=date_raport)

        rt = RichText()
        rt.add(
            f"Дійсним доповідаю, що ...",
            font=WORD_FONT,
            size=WORD_SIZE,
        )

        context.text = rt

        return context
