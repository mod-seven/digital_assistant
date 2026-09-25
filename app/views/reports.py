from datetime import datetime

import flet as ft

from app.components.sidebar import Sidebar
from app.services.report_generation import ReportGeneration
from app.state import AppState
from app.styles import (
    BG_COLOR,
    BORDER,
    CARD_RADIUS,
    CONTENT_PADDING,
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
)


class ReportsView:

    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state

        self.report_type = None

        self.report_type_dropdown = None
        self.form_container = None

    def build(self):

        self.report_type_dropdown = ft.Dropdown(
            label="Тип рапорту",
            hint_text="Оберіть тип рапорту",
            options=[
                ft.DropdownOption(
                    key="report_over_position",
                    text="Рапорт посаду здав",
                ),
                # ft.DropdownOption(
                #     key="business_trip",
                #     text="Рапорт на відрядження",
                # ),
                # ft.DropdownOption(
                #     key="treatment",
                #     text="Рапорт на лікування",
                # ),
            ],
            on_select=self.report_type_changed,
        )

        self.form_container = ft.Container(
            content=self.empty_form(),
            expand=True,
        )

        content = ft.Column(
            controls=[
                ft.Text(
                    "Рапорти",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Text(
                    "Створення та генерація службових документів",
                    size=14,
                    color=TEXT_SECONDARY,
                ),
                ft.Container(
                    content=self.report_type_dropdown,
                    padding=20,
                    bgcolor=WHITE,
                    border_radius=CARD_RADIUS,
                ),
                self.form_container,
            ],
            spacing=20,
            expand=True,
        )

        return ft.Row(
            controls=[
                Sidebar(self.page).build(),
                ft.Container(
                    content=content,
                    expand=True,
                    padding=CONTENT_PADDING,
                    bgcolor=BG_COLOR,
                ),
            ],
            expand=True,
        )

    # ---------------------------------------------------------
    # ЗМІНА ТИПУ РАПОРТУ
    # ---------------------------------------------------------

    def report_type_changed(self, e):

        self.report_type = e.control.value

        print(self.report_type)

        if self.report_type == "report_over_position":
            self.form_container.content = self.report_over_position_form()

        elif self.report_type == "business_trip":
            self.form_container.content = self.business_trip_form()

        elif self.report_type == "treatment":
            self.form_container.content = self.treatment_form()

        self.page.update()

    # ---------------------------------------------------------
    # ПУСТА ФОРМА
    # ---------------------------------------------------------

    def empty_form(self):

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.DESCRIPTION_OUTLINED,
                        size=50,
                        color=TEXT_SECONDARY,
                    ),
                    ft.Text(
                        "Оберіть тип рапорту",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        "Після вибору типу тут з'являться " "необхідні параметри.",
                        color=TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
        )

    # ---------------------------------------------------------
    # ЗАГАЛЬНІ ПОЛЯ
    # ---------------------------------------------------------

    def person_fields(self):

        self.tax_id = ft.TextField(
            label="РНОКПП",
            hint_text="Введіть РНОКПП",
            expand=True,
        )

        self.full_name = ft.TextField(
            label="ПІБ",
            hint_text="Буде заповнено автоматично",
            read_only=True,
            expand=True,
        )

        self.position = ft.TextField(
            label="Посада",
            hint_text="Буде заповнено автоматично",
            read_only=True,
            expand=True,
        )

        return [
            ft.Row(
                controls=[
                    self.tax_id,
                    ft.Button(
                        "Знайти",
                        icon=ft.Icons.SEARCH,
                        on_click=self.find_person,
                    ),
                ],
                spacing=10,
            ),
            ft.Row(
                controls=[
                    self.full_name,
                    self.position,
                ],
                spacing=15,
            ),
        ]

    def report_over_position_form(self):

        self.date_report = ft.TextField(
            label="Дата рапорту",
            hint_text="ДД.ММ.РРРР",
            value=datetime.now().strftime("%d.%m.%Y"),
            expand=True,
        )

        return self.form_card(
            title="Рапорт посаду здав",
            controls=[
                *self.person_fields(),
                ft.Divider(
                    color=BORDER,
                ),
                ft.Row(
                    controls=[
                        self.date_report,
                    ],
                ),
                self.action_buttons(),
            ],
        )

    # ---------------------------------------------------------
    # ВІДРЯДЖЕННЯ
    # ---------------------------------------------------------

    def business_trip_form(self):

        self.destination = ft.TextField(
            label="Місце відрядження",
            hint_text="Населений пункт / підрозділ",
        )

        self.trip_date_from = ft.TextField(
            label="Дата початку",
            hint_text="ДД.ММ.РРРР",
            expand=True,
        )

        self.trip_date_to = ft.TextField(
            label="Дата закінчення",
            hint_text="ДД.ММ.РРРР",
            expand=True,
        )

        self.trip_reason = ft.TextField(
            label="Мета відрядження",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )

        return self.form_card(
            title="Рапорт на відрядження",
            controls=[
                *self.person_fields(),
                ft.Divider(
                    color=BORDER,
                ),
                self.destination,
                ft.Row(
                    controls=[
                        self.trip_date_from,
                        self.trip_date_to,
                    ],
                    spacing=15,
                ),
                self.trip_reason,
                self.action_buttons(),
            ],
        )

    # ---------------------------------------------------------
    # ЛІКУВАННЯ
    # ---------------------------------------------------------

    def treatment_form(self):

        self.medical_institution = ft.TextField(
            label="Медичний заклад",
            hint_text="Назва медичного закладу",
        )

        self.treatment_date = ft.TextField(
            label="Дата",
            hint_text="ДД.ММ.РРРР",
        )

        self.treatment_reason = ft.TextField(
            label="Підстава",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )

        return self.form_card(
            title="Рапорт на лікування",
            controls=[
                *self.person_fields(),
                ft.Divider(
                    color=BORDER,
                ),
                self.medical_institution,
                self.treatment_date,
                self.treatment_reason,
                self.action_buttons(),
            ],
        )

    # ---------------------------------------------------------
    # КАРТКА ФОРМИ
    # ---------------------------------------------------------

    def form_card(self, title, controls):

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Divider(
                        color=BORDER,
                    ),
                    *controls,
                ],
                spacing=15,
            ),
            padding=25,
            bgcolor=WHITE,
            border_radius=CARD_RADIUS,
            expand=True,
        )

    # ---------------------------------------------------------
    # КНОПКИ
    # ---------------------------------------------------------

    def action_buttons(self):

        return ft.Row(
            controls=[
                ft.Button(
                    "Очистити",
                    icon=ft.Icons.CLEAR,
                    on_click=self.clear_form,
                ),
                ft.Button(
                    "Згенерувати рапорт",
                    icon=ft.Icons.DESCRIPTION,
                    on_click=self.generate_report,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        )

    # ---------------------------------------------------------
    # ПОШУК ВІЙСЬКОВОСЛУЖБОВЦЯ
    # ---------------------------------------------------------

    def find_person(self, e):

        tax_id = self.tax_id.value.strip()

        if not tax_id:
            return

        repository = self.state.personnel_repository

        if not repository:
            self.show_message("Спочатку завантажте Excel файл.")
            return

        try:

            person = repository.get_person_by_tax_id(tax_id)

            self.full_name.value = str(person.get("ПІБ", ""))

            self.position.value = str(person.get("Посада", ""))

            self.page.update()

        except Exception as error:

            self.show_message(str(error))

    # ---------------------------------------------------------
    # ОЧИСТИТИ
    # ---------------------------------------------------------

    def clear_form(self, e):

        self.page.controls.clear()

        from app.router import AppRouter

        AppRouter(
            self.page,
            self.state,
        ).route_change()

    # ---------------------------------------------------------
    # ГЕНЕРАЦІЯ
    # ---------------------------------------------------------

    async def generate_report(self, e):
        file_picker = ft.FilePicker()

        file_path = await file_picker.save_file(
            dialog_title="Зберегти рапорт",
            file_name="Рапорт.docx",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx"],
        )

        if not file_path:
            return

        try:
            report_generation = ReportGeneration(
                repository=self.state.personnel_repository,
                path_save_report=file_path,
            )

            context = report_generation.get_context_report_over_position(
                tax_id=self.tax_id.value.strip()
            )

            report_generation.generate_reports(contexts=[context])

            self.show_message(f"Рапорт збережено:\n{file_path}")

        except Exception as ex:
            self.show_message(f"Помилка генерації рапорту: {ex}")

    # ---------------------------------------------------------
    # ПОВІДОМЛЕННЯ
    # ---------------------------------------------------------

    def show_message(self, message):

        dialog = ft.AlertDialog(
            title=ft.Text("Рапорт"),
            content=ft.Text(message),
        )

        self.page.show_dialog(dialog)
